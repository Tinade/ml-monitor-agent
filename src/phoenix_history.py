import os
from phoenix.client import Client

PHOENIX_BASE_URL = "https://app.phoenix.arize.com/s/tsiged87"

def get_job_history(job_id: str) -> str:
    """Query Phoenix traces for past decisions on a specific job."""
    try:
        client = Client(
            base_url=PHOENIX_BASE_URL,
            api_key=os.environ.get("PHOENIX_API_KEY", "")
        )
        spans = client.spans.get_spans_dataframe(
            project_name="ml-monitor-agent",
            timeout=30
        )

        # Filter spans for this job
        job_spans = spans[spans['attributes.job_id'] == job_id]

        if job_spans.empty:
            return f"No history found in Phoenix for {job_id}"

        # Get status spans
        status_spans = job_spans[job_spans['attributes.status'].notna()]
        # Get action spans
        action_spans = job_spans[job_spans['attributes.action'].notna()]

        summary = f"Phoenix trace history for {job_id}:\n"

        for _, row in status_spans.head(3).iterrows():
            summary += f"- Status check: {row['attributes.status']}\n"

        for _, row in action_spans.head(3).iterrows():
            summary += f"- Action taken: {row['attributes.action']}\n"

        return summary

    except Exception as e:
        return f"Could not query Phoenix: {str(e)}"

if __name__ == "__main__":
    print(get_job_history("job_002"))