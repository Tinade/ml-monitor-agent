import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import asyncio
import uuid
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from agent import run_scenario, DECISION_HISTORY
from tools import get_scenarios
app = FastAPI(title="ML Monitor Agent")

# Store results
RESULTS = {}

async def run_all_scenarios(job_id: str):
    all_scores = {}
    for scenario_name, scenario_jobs in SCENARIOS.items():
        scores = await run_scenario(scenario_name, scenario_jobs)
        all_scores[scenario_name] = [
            {"job_id": s["job_id"], "score": s["score"], "correct": s["correct"]}
            for s in scores
        ] if scores else []
    RESULTS[job_id] = {"status": "complete", "results": all_scores}

@app.get("/")
async def root():
    return {"status": "ml-monitor-agent running", "endpoints": ["/dashboard", "/run", "/status/{job_id}", "/health"]}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    with open(os.path.join(BASE_DIR, "web", "dashboard.html")) as f:
        return f.read()


@app.get("/status/{job_id}")
async def status(job_id: str):
    result = RESULTS.get(job_id)
    if not result:
        return {"status": "not_found"}
    return result

@app.get("/run")
async def run():
    all_scores = {}
    for scenario_name, scenario_jobs in get_scenarios().items():
        scores = await run_scenario(scenario_name, scenario_jobs)
        all_scores[scenario_name] = [
            {"job_id": s["job_id"], "score": s["score"], "correct": s["correct"]}
            for s in scores
        ] if scores else []
    return {"results": all_scores}
