# ML Monitor Agent — Self-Healing ML Infrastructure

> ML training jobs fail silently at 3am. On-call engineers get paged to check logs, restart jobs, and document decisions — work that should be automated. This agent does all of that autonomously, learns from every decision, and gets smarter every run.

## Live Demo

**[https://ml-monitor-agent-304908217927.us-central1.run.app/dashboard](https://ml-monitor-agent-304908217927.us-central1.run.app/dashboard)**

Click **Run Agent Now** to watch the agent monitor jobs, detect anomalies, read real Phoenix trace history, and evaluate its own decisions in real time.

**[View Live Phoenix Traces](https://app.phoenix.arize.com/s/tsiged87/projects/UHJvamVjdDoz/traces)**

---

## What It Does

1. **Monitor** — checks all ML training jobs using `check_job_status()`
2. **Detect** — flags jobs with high loss and low progress as AT RISK before they fail
3. **Learn** — queries real Arize Phoenix traces via REST API before every decision
4. **Act** — restarts failed or stalled jobs with justified reasoning
5. **Evaluate** — scores every decision 1-10 using Gemini as an independent LLM-as-Judge
6. **Improve** — accumulates decision history across runs, getting smarter each time

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ML Monitor Agent                          │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌─────────────────────┐     │
│  │models.py │    │ tools.py │    │     agent.py        │  │
│  │ Job class│───▶│ JOBS     │───▶│ Google ADK Agent    │  │
│  │ health   │    │ SCENARIOS│    │ Gemini 2.5 Flash    │  │
│  │ at_risk  │    │ check_   │    │                     │  │
│  │ restart  │    │ job_stat │    │ 1. Read Phoenix     │  │
│  └──────────┘    │ restart  │    │    trace history    │  │
│                  └──────────┘    │ 2. Check job status │  │
│  ┌──────────┐                    │ 3. Detect anomalies │  │
│  │phoenix_  │───────────────────▶│ 4. Restart if needed│  │
│  │history.py│                    │ 5. Explain decision │  │
│  │Phoenix   │                    └──────────┬──────────┘  │
│  │REST API  │                               │             │
│  └──────────┘                               ▼             │
│                                    ┌─────────────────────┐ │
│  ┌──────────┐                      │   evaluator.py      │ │
│  │ Arize    │◀─────────────────────│ LLM-as-Judge        │ │
│  │ Phoenix  │   OpenTelemetry      │ Gemini scores 1-10  │ │
│  │ Cloud    │   Traces             └─────────────────────┘ │
│  └──────────┘                                              │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌─────────────────────┐  │
│  │server.py │    │dashboard │    │ Google Cloud Run     │  │
│  │ FastAPI  │───▶│ .html    │    │ Live URL             │  │
│  │ /run     │    │ Chart.js │    │ ml-monitor-agent-    │  │
│  │ /health  │    │ Scores   │    │ 304908217927...      │  │
│  │ /clear   │    │ Reasoning│    └─────────────────────┘  │
│  └──────────┘    └──────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Scenario Results

| Scenario | Description | Avg Score |
|---|---|---|
| Baseline | job_001 running, job_002 stalled, job_003 failed | 9.3/10 |
| Harder | All jobs stalled or failed | 9.0/10 |
| Complex | Mixed failures with anomaly detection | 9.0/10 |

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | Google ADK |
| LLM | Gemini 2.5 Flash |
| Observability | Arize Phoenix + OpenTelemetry |
| Trace History | Phoenix REST API (arize-phoenix-client) |
| Self-improvement | Phoenix MCP Server |
| Evaluation | LLM-as-Judge |
| API | FastAPI + uvicorn |
| Deployment | Google Cloud Run |
| Testing | pytest — 14 automated tests |

---

## How to Run

```bash
git clone https://github.com/Tinade/ml-monitor-agent
cd ml-monitor-agent
source start.sh
PYTHONPATH=$(pwd) uvicorn src.server:app --host 0.0.0.0 --port 8080
```

Or visit the live dashboard:
**[https://ml-monitor-agent-304908217927.us-central1.run.app/dashboard](https://ml-monitor-agent-304908217927.us-central1.run.app/dashboard)**

---

## Project Structure

```
ml-monitor-agent/
├── src/
│   ├── agent.py           # Main agent with self-improvement loop
│   ├── tools.py           # Job data and tool functions
│   ├── models.py          # Job class with health score and anomaly detection
│   ├── evaluator.py       # LLM-as-Judge evaluator
│   ├── phoenix_history.py # Real Phoenix trace history via REST API
│   └── server.py          # FastAPI web server
├── tests/
│   └── test_models.py     # 14 pytest tests
├── web/
│   └── dashboard.html     # Interactive dashboard with Chart.js
├── Dockerfile
├── start.sh
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Key Features

- **Real Phoenix Trace History** — agent queries actual Arize Phoenix spans via REST API before every decision
- **Anomaly Detection** — detects at-risk jobs before they fail using loss and progress metrics
- **LLM-as-Judge** — independent Gemini evaluation scores every decision 1-10
- **Health Score 0-100** — composite job health metric visible on dashboard
- **Score Progression Chart** — visual proof of agent learning across runs
- **Agent Reasoning Log** — full transparency into every decision

---

Built for the Google Cloud Rapid Agent Hackathon 2026 — Arize Phoenix Track
