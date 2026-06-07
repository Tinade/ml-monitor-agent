JOBS = {"job_001": {"status": "running", "progress": 45, "loss": 0.82},
    "job_002": {"status": "stalled", "progress": 12, "loss": 0.99},
    "job_003": {"status": "failed",  "progress": 0,  "loss": None},
}

def check_job_status(job_id: str) -> dict:
    """Check the current status of an ML training job."""
    job = JOBS.get(job_id)
    if not job:
        return {"error": f"Job {job_id} not found"}
    return {"job_id": job_id, **job}


def restart_job(job_id:str)->dict:
    """ Restarts Stalled or Failed Ml traing Job"""
    if job_id in JOBS:
        JOBS[job_id]["status"] = "restarted"
        return {"job_id": job_id, "action": "restarted", "success": True}
    return {"error": f"Job {job_id} not found"}


       
    class Job:
        def __init__(self, job_id: str, status: str, progress: int, loss: float) -> None:
            self.job_id = job_id
            self.status = status
            self.progress = progress
            self.loss = loss

        def is_healthy(self) -> bool:
            return self.status == "running"

        def restart(self) -> dict:
            if self.status in ["stalled", "failed"]:
                self.status = "restarted"
                return {"job_id": self.job_id, "action": "restarted", "success": True}
            return {"job_id": self.job_id, "action": "skipped", "success": False, "reason": "job is healthy"}

        def to_dict(self) -> dict:
            return {
                "job_id": self.job_id,
                "status": self.status,
                "progress": self.progress,
                "loss": self.loss,
            }

        @staticmethod
        def valid_statuses() -> list:
            return ["running", "stalled", "failed", "restarted"]
    
job = {
    "job_001": {"status": "running", "progress": 45, "loss": 0.82},
    "job_002": {"status": "stalled", "progress": 12, "loss": 0.99},
    "job_003": {"status": "failed",  "progress": 0,  "loss": None},
}   
if __name__ == "__main__":
        job = Job("job_001", "stalled", 12, 0.99)
        print(job.is_healthy())
        print(job.restart())
        print(job.to_dict())
        print(Job.valid_statuses())