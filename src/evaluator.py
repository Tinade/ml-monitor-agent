import json
from google import genai

def evaluate_decision(job_id: str, job_status: dict, action: str, outcome: dict) -> dict:
    """Evaluate the correctness of an agent decision using Gemini as an independent judge."""
    
    prompt = f"""
You are an ML infrastructure evaluation expert.

Job ID: {job_id}
Status before action: {job_status}
Action taken: {action}
Outcome: {outcome}

Was this the correct action?
Rate the decision from 1 to 10.
Explain your reasoning in one sentence.

Respond in JSON only with this format:
{{
    "score": <number 1-10>,
    "correct": <true or false>,
    "reasoning": "<one sentence>"
}}
"""
    client = genai.Client(
            vertexai=True,
            project="project-8a87dc48-0f93-4056-a1c",
            location="us-central1",
        )

    response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    result = json.loads(raw)
    result["job_id"] = job_id
    return result
if __name__ == "__main__":
    result = evaluate_decision(
        job_id="job_002",
        job_status={"status": "stalled", "progress": 12, "loss": 0.99},
        action="restart_job",
        outcome={"success": True}
    )
    print(result)