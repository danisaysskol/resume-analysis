import os
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner
import json

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI()

# Helper: extract skills from text using OpenAI

def extract_skills(text, taxonomy):
    prompt = f"""
Given the following text, extract all relevant skills (from the taxonomy below) and estimate proficiency if possible.\n
Text: {text}\n
Skills Taxonomy: {', '.join(t['name'] for t in taxonomy)}\n
Return a JSON list of extracted skills, each with a proficiency level if possible.
"""
    response = client.responses.create(
        model="gpt-4.1",
        input=prompt
    )
    # According to OpenAI v1, use response.output[0].content[0].text
    try:
        text = response.output[0].content[0].text.strip()
        # Remove markdown code block if present
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        # Only parse the first JSON array in the output
        if '[' in text and ']' in text:
            start = text.index('[')
            end = text.index(']', start) + 1
            text = text[start:end]
        # Remove inline // comments from JSON
        import re
        text = re.sub(r'//.*', '', text)
        return json.loads(text)
    except Exception as e:
        print(f"Error parsing skills from response: {e}\nRaw response: {getattr(response, 'output', None)}")
        return []

# Agent-based gap analysis
def skill_gap_analysis(user_skills, job_skills):
    user_skill_names = {s['skill'] for s in user_skills}
    job_skill_names = {s['skill'] for s in job_skills}
    missing = job_skill_names - user_skill_names
    existing = user_skill_names & job_skill_names
    return {
        "missing_skills": [s for s in job_skills if s['skill'] in missing],
        "existing_skills": [s for s in user_skills if s['skill'] in existing]
    }
