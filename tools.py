from models import Job
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