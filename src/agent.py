import os
import asyncio
from evaluator import evaluate_decision
from phoenix.otel import register
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from tools import JOBS, check_job_status, restart_job
import tools
from models import Job
from tools import JOBS, check_job_status, restart_job, get_scenarios
from phoenix_history import get_job_history

# --- Decision History ---
DECISION_HISTORY = []

# --- Phoenix Tracing Setup ---
tracer_provider = register(
    project_name="ml-monitor-agent",
    auto_instrument=False,
)
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)

# --- Phoenix MCP Toolset ---
phoenix_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@arizeai/phoenix-mcp@latest",
                "--baseUrl", "https://app.phoenix.arize.com/s/tsiged87",
                "--apiKey", os.environ.get("PHOENIX_API_KEY", ""),
            ],
        )
    )
)

# --- Agent Definition ---
agent = Agent(
    name="ml_monitor_agent",
    model="gemini-2.5-flash",
    description="Monitors ML training jobs and takes corrective action.",
    instruction="""You are an ML infrastructure monitoring agent.

    STEP 1 — READ THE HISTORY PROVIDED:
    History is provided directly in this message under PAST DECISION HISTORY.
    Read it carefully before acting. No need to search Phoenix.

    STEP 2 — CHECK JOB STATUS:
    Use check_job_status for each job to get current status.

    STEP 3 — DECIDE BASED ON HISTORY + CURRENT STATUS:

    If the job is stalled or failed:

        - If history shows restart attempts were successful:
            restart the job and explain why

        - If history shows multiple restart attempts failed:
            do NOT restart
            recommend escalation to an engineer

        - If no history exists:
            restart as the default action

    If the job is running BUT at_risk is True:

        - If history shows proactive restart improved outcomes:
            restart proactively

        - Otherwise:
            warn the user and continue monitoring

    If the job is running and at_risk is False:
        do nothing

    STEP 4 — EXPLAIN YOUR DECISION:
    Always state:
    - What history you found in Phoenix
    - What the current status is
    - What action you took and why""",
    tools=[check_job_status, restart_job, phoenix_mcp],
)

async def run_scenario(
    scenario_name: str,
    scenario_jobs: dict,
    use_history: bool = True
) -> list:
    """Run the agent on a specific scenario and return evaluation scores."""

    # Always create fresh Job objects to prevent mutation carry-over
    fresh_jobs = {
        job_id: Job(job.job_id, job.status, job.progress, job.loss)
        for job_id, job in scenario_jobs.items()
    }
    tools.JOBS.clear()
    tools.JOBS.update(fresh_jobs)

    print(f"\n{'='*50}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*50}\n")

    # Capture original states
    original_states = {job_id: job.to_dict() for job_id, job in tools.JOBS.items()}

    history_summary = ""

    if use_history:
        phoenix_traces = ""

        for job_id in ["job_001", "job_002", "job_003"]:
            trace_data = get_job_history(job_id, DECISION_HISTORY)
            phoenix_traces += f"\n{trace_data}"

        history_summary = (
            f"\n\nPHOENIX TRACE HISTORY "
            f"(real observability data):\n{phoenix_traces}"
        )
    else:
        history_summary = (
            "\n\nNO PHOENIX HISTORY AVAILABLE. "
            "Make decisions using only current job status."
        )

    # Run agent
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="ml-monitor-agent",
        user_id="engineer-1",
    )
    runner = Runner(
        agent=agent,
        app_name="ml-monitor-agent",
        session_service=session_service,
    )
    message = Content(
        role="user",
        parts=[Part(text=f"""For each job (job_001, job_002, job_003):
1. Check the current job status
2. If stalled or failed, restart it
3. Explain your decision using the history below{history_summary}

If no history exists yet, say "no history found, restarting as default action." """)]
    )
    agent_response = ""
    try:
        async for event in runner.run_async(
            user_id="engineer-1",
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response():
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            agent_response = part.text
                            print("Agent:", part.text)
    except Exception as e:
        print(f"Agent run failed for {scenario_name}: {str(e)}")

    # Evaluate decisions
    scores = []
    print(f"\n--- Evaluating {scenario_name} ---\n")
    for job_id, job in tools.JOBS.items():
        original = original_states[job_id]
    action = "restart_job" if job.status == "restarted" else "do_nothing"

    success = False

    # job_003 is our escalation scenario
    if job_id == "job_003":

        if action == "do_nothing":
            success = True

    # normal restart behavior
    elif original["status"] in ["failed", "stalled"]:

        if action == "restart_job":
            success = True

    # healthy running jobs should be left alone
    elif original["status"] == "running":

        if action == "do_nothing":
            success = True
        try:
            evaluation = evaluate_decision(
                job_id=job_id,
                job_status=original,
                action=action,
                outcome=outcome
            )
            scores.append(evaluation)
            DECISION_HISTORY.append({
                "scenario": scenario_name,
                "job_id": job_id,
                "original_status": original["status"],
                "action": action,
                "score": evaluation["score"],
                "correct": evaluation["correct"]
            })
            print(f"{job_id}: score={evaluation['score']}/10 correct={evaluation['correct']}")
        except Exception as e:
            print(f"Evaluation failed for {job_id}: {str(e)}")

    return scores, agent_response

async def main():
    all_runs = []

    for run_number in range(1, 6):
        print(f"\n{'='*50}")
        print(f"RUN {run_number} OF 5")
        print(f"{'='*50}")

        run_scores = {"run": run_number}
        for scenario_name, scenario_jobs in get_scenarios().items():
            scores, _ = await run_scenario(scenario_name, scenario_jobs)
            avg = sum(s["score"] for s in scores) / len(scores) if scores else 0
            run_scores[scenario_name] = round(avg, 1)

        all_runs.append(run_scores)

    # Print progression table
    print(f"\n{'='*50}")
    print("SCORE PROGRESSION ACROSS 5 RUNS")
    print(f"{'='*50}")
    print(f"{'Run':<6} {'Baseline':<12} {'Harder':<12} {'Complex':<12}")
    for r in all_runs:
        print(f"{r['run']:<6} {r['Baseline']:<12} {r['Harder']:<12} {r['Complex']:<12}")

if __name__ == "__main__":
    asyncio.run(main())


