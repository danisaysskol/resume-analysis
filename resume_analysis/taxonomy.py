import json
from pathlib import Path

TAXONOMY_FILE = Path("data/skills_taxonomy.json")

def load_taxonomy():
    with open(TAXONOMY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_taxonomy(taxonomy):
    with open(TAXONOMY_FILE, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, indent=2, ensure_ascii=False)
