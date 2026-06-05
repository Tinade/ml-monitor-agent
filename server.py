import asyncio
from fastapi import FastAPI
from agent import run_scenario, DECISION_HISTORY
from tools import SCENARIOS

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ml-monitor-agent running", "endpoints": ["/run", "/health"]}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/run")
async def run():
    all_scores = {}
    for scenario_name, scenario_jobs in SCENARIOS.items():
        scores = await run_scenario(scenario_name, scenario_jobs)
        all_scores[scenario_name] = scores
    return {"results": all_scores}
