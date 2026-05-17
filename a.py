import os
import asyncio

from phoenix.otel import register
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google.genai.types import Content, Part

# ---------------------------------------------------
# Phoenix / OpenTelemetry Tracing Setup
# ---------------------------------------------------

tracer_provider = register(
    project_name="ml-monitor-agent",
    auto_instrument=False,
)

GoogleADKInstrumentor().instrument(
    tracer_provider=tracer_provider
)

# ---------------------------------------------------
# Mock ML Job Database
# ---------------------------------------------------

JOBS = {
    "job_001": {
        "status": "running",
        "progress": 45,
        "loss": 0.82,
    },
    "job_002": {
        "status": "stalled",
        "progress": 12,
        "loss": 0.99,
    },
    "job_003": {
        "status": "failed",
        "progress": 0,
        "loss": None,
    },
}

# ---------------------------------------------------
# Agent Tools
# ---------------------------------------------------

def check_job_status(job_id: str) -> dict:
    """
    Check the current status of an ML training job.
    """

    job = JOBS.get(job_id)

    if not job:
        return {
            "error": f"Job {job_id} not found"
        }

    return {
        "job_id": job_id,
        **job,
    }


def restart_job(job_id: str) -> dict:
    """
    Restart a failed or stalled ML training job.
    """

    if job_id not in JOBS:
        return {
            "error": f"Job {job_id} not found"
        }

    JOBS[job_id]["status"] = "restarted"

    return {
        "job_id": job_id,
        "action": "restarted",
        "success": True,
    }

# ---------------------------------------------------
# Agent Definition
# ---------------------------------------------------

agent = Agent(
    name="ml_monitor_agent",
    model="gemini-2.5-flash",
    description="Monitors ML training jobs and takes corrective action.",
    instruction="""
You are an ML infrastructure monitoring agent.

When asked to check jobs:
1. Use check_job_status for each job.
2. If a job is stalled or failed, automatically call restart_job.
3. Explain what you found.
4. Explain what corrective action you took.
""",
    tools=[
        check_job_status,
        restart_job,
    ],
)

# ---------------------------------------------------
# Main Async Runner
# ---------------------------------------------------

async def main():

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

    print("\n--- ML Monitor Agent Starting ---\n")

    message = Content(
        role="user",
        parts=[
            Part(
                text="Check all jobs: job_001, job_002, job_003 and fix any issues."
            )
        ],
    )

    async for event in runner.run_async(
        user_id="engineer-1",
        session_id=session.id,
        new_message=message,
    ):

        # Debug: see event structure
        print(f"\n[DEBUG EVENT TYPE]: {type(event)}")

        if event.is_final_response():

            if hasattr(event, "content") and event.content:

                for part in event.content.parts:

                    if hasattr(part, "text") and part.text:

                        print("\nAgent Response:\n")
                        print(part.text)

# ---------------------------------------------------
# Entry Point
# ---------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
