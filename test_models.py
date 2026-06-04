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

def test_to_dict():
    job = Job("job_001", "running", 45, 0.82)
    result = job.to_dict()
    assert result["job_id"] == "job_001"
    assert result["status"] == "running"
    assert result["progress"] == 45
    assert result["loss"] == 0.82
      
def test_valid_statuses():
    result = Job.valid_statuses()
    assert result == ["running", "stalled", "failed", "restarted"]
    