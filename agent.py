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
from models import Job

# --- Phoenix Tracing Setup ---
tracer_provider = register(
    project_name="ml-monitor-agent",
    auto_instrument=False,
)
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)


JOBS = {
    "job_001": Job("job_001", "running", 45, 0.82),
    "job_002": Job("job_002", "stalled", 12, 0.99),
    "job_003": Job("job_003", "failed", 0, None),
}

# --- Test Scenarios ---
SCENARIOS = {
    "Baseline": {
        "job_001": Job("job_001", "running", 45, 0.82),
        "job_002": Job("job_002", "stalled", 12, 0.99),
        "job_003": Job("job_003", "failed",  0,  None),
    },
    "Harder": {
        "job_001": Job("job_001", "stalled", 30, 0.95),
        "job_002": Job("job_002", "failed",  0,  None),
        "job_003": Job("job_003", "failed",  0,  None),
    },
    "Complex": {
        "job_001": Job("job_001", "failed",  0,  None),
        "job_002": Job("job_002", "failed",  0,  None),
        "job_003": Job("job_003", "stalled", 5,  0.98),
    },
}
# --- Agent Tools ---
def check_job_status(job_id: str) -> dict:
    """Check the current status of an ML training job."""
    job = JOBS.get(job_id)
    if not job:
        return {"error": f"Job {job_id} not found"}
    try:
        return job.to_dict()
    except Exception as e:
        return {"error": f"Failed to read job {job_id}: {str(e)}"}

def restart_job(job_id: str) -> dict:
    """Restart a failed or stalled ML training job."""
    job = JOBS.get(job_id)
    if not job:
        return {"error": f"Job {job_id} not found"}
    try:
        return job.restart()
    except Exception as e:
        return {"error": f"Failed to restart job {job_id}: {str(e)}"}

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
    When asked to check jobs, use check_job_status for each job.
    If a job is stalled or failed, automatically call restart_job.
    Before acting, query your past traces using Phoenix MCP tools to learn from previous decisions.
    Always explain what you found, what history you consulted, and what action you took.""",
    tools=[check_job_status, restart_job, phoenix_mcp],
)
# Capture original job states before agent acts
async def run_scenario(scenario_name: str, scenario_jobs: dict) -> list:
    """Run the agent on a specific scenario and return evaluation scores."""
    
    # Update global JOBS with scenario data
    global JOBS
    JOBS.clear()
    JOBS.update(scenario_jobs)
    
    print(f"\n{'='*50}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*50}\n")
    
    # Capture original states
    original_states = {job_id: job.to_dict() for job_id, job in JOBS.items()}
    
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
        parts=[Part(text="Check all jobs: job_001, job_002, job_003 and fix any issues.")]
    )
    async for event in runner.run_async(
        user_id="engineer-1",
        session_id=session.id,
        new_message=message,
    ):
        if event.is_final_response():
            if hasattr(event, 'content') and event.content:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print("Agent:", part.text)

    # Evaluate decisions
    scores = []
    print(f"\n--- Evaluating {scenario_name} ---\n")
    for job_id, job in JOBS.items():
        original = original_states[job_id]
        action = "restart_job" if job.status == "restarted" else "do_nothing"
        outcome = {"success": True}
        evaluation = evaluate_decision(
            job_id=job_id,
            job_status=original,
            action=action,
            outcome=outcome
        )
        scores.append(evaluation)
        print(f"{job_id}: score={evaluation['score']}/10 correct={evaluation['correct']}")
    
    return scores
async def main():
    all_scores = {}
    
    for scenario_name, scenario_jobs in SCENARIOS.items():
        scores = await run_scenario(scenario_name, scenario_jobs)
        all_scores[scenario_name] = scores
    
    # --- Print Comparison Table ---
    print(f"\n{'='*50}")
    print("RESULTS ACROSS ALL SCENARIOS")
    print(f"{'='*50}\n")
    
    for scenario_name, scores in all_scores.items():
        avg = sum(s['score'] for s in scores) / len(scores)
        print(f"{scenario_name}: avg score = {avg:.1f}/10")

if __name__ == "__main__":
    asyncio.run(main())