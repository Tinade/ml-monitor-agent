from models import Job

def test_is_healthy_when_running():
    job = Job("job_001", "running", 45, 0.82)
    assert job.is_healthy() == True