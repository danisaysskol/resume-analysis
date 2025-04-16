import json
from resume_analysis.taxonomy import load_taxonomy
from resume_analysis.skill_analysis import extract_skills, skill_gap_analysis
from resume_analysis.models import *
from resume_analysis.skill_analysis import *
from resume_analysis.taxonomy import *
from resume_analysis.db_utils import *
import sys
from pathlib import Path
from markitdown import MarkItDown

DATA_DIR = Path("db")
RESUME_PDF = "db/resume.pdf"
JOB_PDF = "db/job_description.pdf"
OUTPUT_FILE = Path("data") / "gap_analysis_output.json"
RESUME_MD = "data/resume.md"
JOB_MD = "data/job_description.md"


# Convert PDF to markdown and extract plain text, saving markdown as well
def pdf_to_text_and_md(pdf_path, md_path):
    md = MarkItDown(enable_plugins=False)
    try:
        result = md.convert(pdf_path)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(result.markdown)
        return result.text_content
    except Exception as e:
        print(f"Error reading or converting {pdf_path}: {e}")
        return None

def main():
    taxonomy = load_taxonomy()
    # Check files exist
    if not Path(RESUME_PDF).exists():
        print(f"ERROR: {RESUME_PDF} not found.")
        sys.exit(1)
    if not Path(JOB_PDF).exists():
        print(f"ERROR: {JOB_PDF} not found.")
        sys.exit(1)
    resume = pdf_to_text_and_md(RESUME_PDF, RESUME_MD)
    job_desc = pdf_to_text_and_md(JOB_PDF, JOB_MD)
    if resume is None or job_desc is None:
        print("ERROR: Could not extract text from one or both PDFs.")
        sys.exit(1)
    user_skills = extract_skills(resume, taxonomy)
    job_skills = extract_skills(job_desc, taxonomy)
    gap = skill_gap_analysis(user_skills, job_skills)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(gap, f, indent=2, ensure_ascii=False)
    print(f"Skill gap analysis complete. Results saved to {OUTPUT_FILE}")
    print(f"Extracted markdown saved as {RESUME_MD} and {JOB_MD}")

if __name__ == "__main__":
    main()
