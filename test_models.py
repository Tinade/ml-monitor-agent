from models import Job
import tools
def test_is_healthy_when_running():
    job = Job("job_001", "running", 45, 0.82)
    assert job.is_healthy() == True

def test_is_healthy_when_stalled():
    job = Job("job_002", "stalled", 12, 0.99)
    assert job.is_healthy() == False

def test_is_healthy_when_failed():
    job = Job("job_002", "failed", 0, None)
    assert job.is_healthy() == False

def test_restart_when_stalled():
    job = Job("job_002", "stalled", 12, 0.99)
    result = job.restart()
    assert result["action"] == "restarted"

def test_restart_when_failed():
    job = Job("job_001", "failed", 0, None)
    result = job.restart()
    assert result["action"] == "restarted"

def test_restart_when_running():
    job = Job("job_001", "running", 45, 0.82)
    result = job.restart()
    assert result["action"] == "skipped"
    