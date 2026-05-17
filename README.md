# ML Monitor Agent

An autonomous ML job monitoring agent that detects failures in distributed 
training pipelines and takes corrective action automatically.

## What it does

- Monitors ML training jobs in real time
- Detects stalled and failed jobs automatically
- Restarts unhealthy jobs without human intervention
- Traces every decision via OpenTelemetry to Arize Phoenix

## Tech Stack

- Google ADK — agent orchestration
- Gemini 2.5 Flash — reasoning engine
- Arize Phoenix — observability and tracing
- OpenTelemetry — distributed tracing
- Python 3.14 — async runtime

## How it works

The agent checks each job status using tools, reasons about what is wrong,
and calls corrective actions automatically. Every decision is traced to 
Arize Phoenix for full observability.

## Run it

```bash
source start.sh
python agent.py
```

## Part of a broader ML infrastructure portfolio

The jobs monitored here are processed by 
[ml-infra-pipeline-lab](https://github.com/Tinade/cloud-systems-lab)
— a distributed job processing engine demonstrating concurrency, 
threading, and retry logic.

## Hackathon

Submitted to Google Cloud Rapid Agent Hackathon 2026 — Arize track.
