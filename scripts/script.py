import sys
import os
from pathlib import Path
from typing import Dict, Any
import tempfile
from mermaid_generator import generate_mermaid_roadmap
import json

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from resume_analysis.taxonomy import load_taxonomy
from resume_analysis.skill_analysis import extract_skills, skill_gap_analysis
from resume_analysis.models import *
from resume_analysis.skill_analysis import *
from resume_analysis.taxonomy import *
from resume_analysis.db_utils import *
from markitdown import MarkItDown
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Resume Analysis API",
    description="API for analyzing skills gap between resumes and job descriptions",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend running on port 5173
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Convert PDF to markdown and extract plain text
def pdf_to_text_and_md(pdf_bytes):
    md = MarkItDown(enable_plugins=False)
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name
        
        result = md.convert(temp_pdf_path)
        
        # Clean up temporary file
        os.unlink(temp_pdf_path)
        
        return {
            "markdown": result.markdown,
            "text_content": result.text_content
        }
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_pdf_path' in locals():
            try:
                os.unlink(temp_pdf_path)
            except:
                pass
        raise e

@app.post("/analyze", response_model=Dict[str, Any])
async def analyze_resume_and_job(
    resume: UploadFile = File(..., description="Resume PDF file"),
    job_description: UploadFile = File(..., description="Job Description PDF file")
):
    """
    Upload a resume and job description PDF to analyze the skill gap.
    Returns the skill gap analysis results.
    """
    try:
        # Load taxonomy
        taxonomy = load_taxonomy()
        
        # Read uploaded files
        resume_content = await resume.read()
        job_description_content = await job_description.read()
        
        # Process PDF files
        resume_data = pdf_to_text_and_md(resume_content)
        job_data = pdf_to_text_and_md(job_description_content)
        
        if not resume_data or not job_data:
            raise HTTPException(status_code=400, detail="Could not extract text from one or both PDFs")
        
        # Extract skills
        user_skills = extract_skills(resume_data["text_content"], taxonomy)
        job_skills = extract_skills(job_data["text_content"], taxonomy)
        
        # Perform gap analysis
        gap_analysis = skill_gap_analysis(user_skills, job_skills)
        
        # Generate roadmap
        roadmap = generate_mermaid_roadmap(gap_analysis)
        print(roadmap)

        # write temp_gap_analysis in the data folder
        import os
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "temp_gap_analysis.txt")
        with open(output_path, "w") as f:
            json.dump({
                "user_skills": user_skills,
                "job_skills": job_skills,
                "gap_analysis": gap_analysis
            }, f)

        # Prepare response
        return {
            "gap_analysis": gap_analysis,
            "user_skills": user_skills,
            "job_skills": job_skills,
            "resume_markdown": resume_data["markdown"],
            "job_markdown": job_data["markdown"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Resume Analysis API. Use /analyze endpoint to analyze resume and job description."}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)