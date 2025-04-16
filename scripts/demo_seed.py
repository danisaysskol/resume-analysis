import uuid
from datetime import datetime
from pathlib import Path
from markitdown import MarkItDown
from resume_analysis.models import (
    UserProfile, JobDescription, SkillTaxonomy, ExtractedSkill, SkillGapReport, SkillGapDetail, Base
)
from resume_analysis.agent_output_models import UserProfileModel, JobDescriptionModel
from resume_analysis.db_utils import create_all_tables, SessionLocal, export_table_to_json
from resume_analysis.taxonomy import load_taxonomy
from resume_analysis.skill_analysis import extract_skills, skill_gap_analysis
import json

def new_id():
    return str(uuid.uuid4())

def pdf_to_text_and_md(pdf_path, md_path):
    md = MarkItDown(enable_plugins=False)
    result = md.convert(pdf_path)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(result.markdown)
    return result.text_content

def seed_and_export():
    create_all_tables()
    session = SessionLocal()

    # --- Load Skill Taxonomy from TXT, convert to JSON, and use parsed taxonomy ---
    import csv
    import ast
    taxonomy_txt_path = "data/skills_taxonomy.txt"
    taxonomy_json_path = "data/skills_taxonomy.json"
    taxonomy = []
    with open(taxonomy_txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  # Skip comments/empty
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 6:
                continue  # Skip malformed
            skill_id, name, category, description, related_skills, source = parts
            # Parse related_skills as list
            try:
                related_skills = ast.literal_eval(related_skills)
            except Exception:
                related_skills = []
            taxonomy.append({
                "skill_id": skill_id,
                "name": name,
                "category": category,
                "description": description,
                "related_skills": related_skills,
                "source": source
            })
    # Write fresh JSON for reference/compatibility
    with open(taxonomy_json_path, "w", encoding="utf-8") as f:
        import json
        json.dump(taxonomy, f, indent=2)
    taxonomy_objs = []
    taxonomy_map = {}
    for t in taxonomy:
        obj = SkillTaxonomy(
            skill_id=t.get("skill_id", new_id()),
            name=t["name"],
            category=t.get("category"),
            description=t.get("description"),
            related_skills=t.get("related_skills"),
            source=t.get("source", "Custom"),
            updated_at=datetime.utcnow(),
        )
        taxonomy_objs.append(obj)
        taxonomy_map[obj.name] = obj.skill_id
        session.merge(obj)
    session.commit()

    # --- Parse resume.pdf and job_description.pdf ---
    resume_text = pdf_to_text_and_md("db/resume.pdf", "data/resume.md")
    job_text = pdf_to_text_and_md("db/job_description.pdf", "data/job_description.md")

    # --- Create UserProfile and JobDescription using OpenAI Agent output_type for structured JSON ---
    from agents import Agent, Runner
    from resume_analysis.agent_output_models import UserProfileModel, JobDescriptionModel
    import json
    # Extract user profile
    user_agent = Agent(
        name="UserProfileExtractor",
        instructions="Extract the user's name, email, and resume text from the following text. Return as JSON.",
        output_type=UserProfileModel
    )
    user_result = Runner.run_sync(user_agent, input=resume_text)
    user_profile = user_result.final_output
    with open("data/user_profiles.json", "w") as f:
        json.dump([user_profile.dict()], f, indent=2)
    user = UserProfile(
        user_id=new_id(),
        name=user_profile.name or "",
        email=user_profile.email or "",
        resume_text=user_profile.resume_text,
        profile_url="",
        created_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()

    # Extract job description
    job_agent = Agent(
        name="JobDescriptionExtractor",
        instructions="Extract the job's title, company,  location, and description text from the following text. Return as JSON.",
        output_type=JobDescriptionModel
    )
    job_result = Runner.run_sync(job_agent, input=job_text)
    job_desc = job_result.final_output
    with open("data/job_descriptions.json", "w") as f:
        json.dump([job_desc.dict()], f, indent=2)
    job = JobDescription(
        job_id=new_id(),
        title=job_desc.title or "",
        company=job_desc.company or "",
        description_text=job_desc.description_text,
        location=job_desc.location or "",
        created_at=datetime.utcnow()
    )
    session.add(job)
    session.commit()

    # --- Extract skills using OpenAI Agents SDK for structured output ---
    from resume_analysis.agent_output_models import ExtractedSkillsList
    # User skills
    user_skills_agent = Agent(
        name="UserSkillsExtractor",
        instructions="Extract all relevant skills (from the taxonomy below) and estimate proficiency if possible. Return as JSON list.",
        output_type=ExtractedSkillsList
    )
    user_skills_result = Runner.run_sync(user_skills_agent, input=resume_text)
    user_skills_list = user_skills_result.final_output.skills
    # Job skills
    job_skills_agent = Agent(
        name="JobSkillsExtractor",
        instructions="Extract all relevant skills (from the taxonomy below) and estimate proficiency if possible. Return as JSON list.",
        output_type=ExtractedSkillsList
    )
    job_skills_result = Runner.run_sync(job_skills_agent, input=job_text)
    job_skills_list = job_skills_result.final_output.skills
    # Store all extracted skills in data/extracted_skills.json
    all_extracted = []
    for s in user_skills_list:
        skill_id = taxonomy_map.get(s.skill, new_id())
        all_extracted.append({
            "source_type": "user_profile",
            "source_id": user.user_id,
            "skill_id": skill_id,
            "raw_text": s.raw_text or s.skill,
            "confidence": s.confidence or 1.0,
            "proficiency": s.proficiency,
        })
    for s in job_skills_list:
        skill_id = taxonomy_map.get(s.skill, new_id())
        all_extracted.append({
            "source_type": "job_description",
            "source_id": job.job_id,
            "skill_id": skill_id,
            "raw_text": s.raw_text or s.skill,
            "confidence": s.confidence or 1.0,
            "proficiency": s.proficiency,
        })
    with open("data/extracted_skills.json", "w") as f:
        json.dump(all_extracted, f, indent=2)
    # Insert into DB
    for s in all_extracted:
        session.add(ExtractedSkill(
            extracted_id=new_id(),
            source_type=s["source_type"],
            source_id=s["source_id"],
            skill_id=s["skill_id"],
            raw_text=s["raw_text"],
            confidence=s["confidence"],
            proficiency=s["proficiency"],
            extracted_at=datetime.utcnow()
        ))
    session.commit()

    # --- Skill Gap Analysis ---
    # Convert Pydantic models to dicts for skill_gap_analysis
    user_skills_dicts = [s.dict() for s in user_skills_list]
    job_skills_dicts = [s.dict() for s in job_skills_list]
    gap = skill_gap_analysis(user_skills_dicts, job_skills_dicts)
    report = SkillGapReport(
        report_id=new_id(),
        user_id=user.user_id,
        job_id=job.job_id,
        generated_at=datetime.utcnow(),
        match_score=0.0,  # Optionally compute
        summary=""  # Optionally fill
    )
    session.add(report)
    session.commit()

    # --- SkillGapDetail ---
    gap_details = []
    for s in gap["existing_skills"]:
        skill_id = taxonomy_map.get(s["skill"], new_id())
        gap_details.append(SkillGapDetail(
            detail_id=new_id(),
            report_id=report.report_id,
            skill_id=skill_id,
            status="Matched",
            user_proficiency=s.get("proficiency"),
            job_proficiency=None,
            similarity_score=1.0,
            notes=""
        ))
    for s in gap["missing_skills"]:
        skill_id = taxonomy_map.get(s["skill"], new_id())
        gap_details.append(SkillGapDetail(
            detail_id=new_id(),
            report_id=report.report_id,
            skill_id=skill_id,
            status="Missing",
            user_proficiency=None,
            job_proficiency=None,
            similarity_score=0.0,
            notes=""
        ))
    for d in gap_details:
        session.add(d)
    session.commit()

    # --- Export each table to JSON ---
    export_table_to_json(session, UserProfile, 'data/user_profiles.json')
    export_table_to_json(session, JobDescription, 'data/job_descriptions.json')
    export_table_to_json(session, SkillTaxonomy, 'data/skill_taxonomy.json')
    export_table_to_json(session, ExtractedSkill, 'data/extracted_skills.json')
    export_table_to_json(session, SkillGapReport, 'data/skill_gap_reports.json')
    export_table_to_json(session, SkillGapDetail, 'data/skill_gap_details.json')
    session.close()

if __name__ == "__main__":
    seed_and_export()
