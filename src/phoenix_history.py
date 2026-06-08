import os
from phoenix.client import Client

PHOENIX_API_KEY = os.environ.get("PHOENIX_API_KEY", "")
PHOENIX_BASE_URL = "https://app.phoenix.arize.com/s/tsiged87"

def get_job_history(job_id: str) -> str:
    """Query Phoenix traces for past decisions on a specific job."""
    try:
        client = Client(
            base_url=PHOENIX_BASE_URL,
            api_key=PHOENIX_API_KEY
        )
        spans = client.spans.get_spans_dataframe(
            project_name="ml-monitor-agent",
            timeout=30
        )
        
        # Filter spans for this job
        job_spans = spans[spans['attributes.job_id'] == job_id][
            ['name', 'attributes.status', 'attributes.action']
        ].dropna()
        
        if job_spans.empty:
            return f"No history found in Phoenix for {job_id}"
        
        # Build summary
        summary = f"Phoenix trace history for {job_id}:\n"
        for _, row in job_spans.head(5).iterrows():
            summary += f"- {row['name']}: status={row['attributes.status']}, action={row['attributes.action']}\n"
        
        return summary
        
    except Exception as e:
        return f"Could not query Phoenix history: {str(e)}"

if __name__ == "__main__":
    print(get_job_history("job_002"))