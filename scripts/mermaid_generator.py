import anthropic
from dotenv import load_dotenv

load_dotenv()

def generate_mermaid_roadmap(skill_gaps):
    """
    Generates a Mermaid roadmap based on the user's skill gaps using the Claude API.

    Parameters:
    - skill_gaps (str): A description of the user's skill gaps.
    - api_key (str): Your Anthropic API key.

    Returns:
    - str: Mermaid code representing the roadmap.
    """
    client = anthropic.Anthropic()

    prompt = (
        "You are an expert career coach and curriculum designer. "
        "Given the following user's skill gaps, generate a detailed learning roadmap in Mermaid diagram format. "
        "Only return the Mermaid code without any additional text or explanation, only code means begin and end with code only, nothing else\n\n"
        f"User's skill gaps:\n{skill_gaps}\n\n"
        "Mermaid code:"
    )

    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=10240,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.content


if __name__ == "__main__":
    # read temp_gap_analysis.txt from data folder
    with open("../data/temp_gap_analysis.txt", "r") as f:
        skill_gaps = f.read()
    roadmap = generate_mermaid_roadmap(skill_gaps)
    roadmap[0].text



