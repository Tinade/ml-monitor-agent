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
        def is_at_risk(self) -> bool:
            if self.loss is not None and self.loss > 0.90 and self.progress < 20:
                return True
            return False

        def health_score(self) -> int:
            health = 100
            if self.status == "stalled":
               health -= 30
            if self.status == "failed":
               health -= 50
            if self.status == "restarted":
               health -= 10
            if self.loss is None:
               health -= 10
            elif self.loss > 0.95:
               health -= 30
            elif self.loss > 0.85:
               health -= 20
            if self.is_at_risk():
               health -= 20
            health = max(0, health)
            return health
if __name__ == "__main__":
    job = Job("job_001", "stalled", 12, 0.99)
    print(job.is_healthy())
    print(job.restart())
    print(job.to_dict())
    print(Job.valid_statuses())
