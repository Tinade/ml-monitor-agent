from models import Job
from opentelemetry import trace
JOBS = {
    "job_001": Job("job_001", "running", 45, 0.82),
    "job_002": Job("job_002", "stalled", 12, 0.99),
    "job_003": Job("job_003", "failed", 0, None),
}

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
def check_job_status(job_id: str) -> dict:
    """Check the current status of an ML training job."""
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(f"check_job_status_{job_id}") as span:
        span.set_attribute("job_id", job_id)
        job = JOBS.get(job_id)
        if not job:
            span.set_attribute("error", "job_not_found")
            return {"error": f"Job {job_id} not found"}
        span.set_attribute("status", job.status)
        span.set_attribute("progress", job.progress)
        try:
            return job.to_dict()
        except Exception as e:
            return {"error": f"Failed to read job {job_id}: {str(e)}"}

def restart_job(job_id: str) -> dict:
    """Restart a failed or stalled ML training job."""
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(f"restart_job_{job_id}") as span:
        span.set_attribute("job_id", job_id)
        job = JOBS.get(job_id)
        if not job:
            span.set_attribute("error", "job_not_found")
            return {"error": f"Job {job_id} not found"}
        try:
            result = job.restart()
            span.set_attribute("action", result["action"])
            return result
        except Exception as e:
            return {"error": f"Failed to restart job {job_id}: {str(e)}"}