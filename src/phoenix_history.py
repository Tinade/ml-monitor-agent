import os
from phoenix.client import Client

PHOENIX_BASE_URL = "https://app.phoenix.arize.com/s/tsiged87"

def get_job_history(job_id: str, decision_history: list = None) -> str:
    """Query Phoenix traces and session history for a specific job."""
    summary = f"Phoenix trace history for {job_id}:\n"

    # Real Phoenix spans
    try:
        client = Client(
            base_url=PHOENIX_BASE_URL,
            api_key=os.environ.get("PHOENIX_API_KEY", "")
        )
        spans = client.spans.get_spans_dataframe(
            project_name="ml-monitor-agent",
            timeout=15
        )
        job_spans = spans[spans['attributes.job_id'] == job_id]

        if not job_spans.empty:
            status_spans = job_spans[job_spans['attributes.status'].notna()]
            action_spans = job_spans[job_spans['attributes.action'].notna()]

            for _, row in status_spans.head(3).iterrows():
                summary += f"- Status check: {row['attributes.status']}\n"
            for _, row in action_spans.head(3).iterrows():
                summary += f"- Action taken: {row['attributes.action']}\n"

    except Exception as e:
        summary += f"- Phoenix query failed: {str(e)}\n"

    # Session history for this job
    if decision_history:
        job_decisions = [h for h in decision_history if h["job_id"] == job_id]
        if job_decisions:
            summary += f"\nSession decision history for {job_id}:\n"
            for d in job_decisions[-3:]:
                summary += (
                f"- {d['scenario']}: "
                f"status={d['original_status']}, "
                f"action={d['action']}, "
                f"success={d['success']}, "
                f"score={d['score']}/10\n"
            )

    return summary

if __name__ == "__main__":
    print(get_job_history("job_002"))