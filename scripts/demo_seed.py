import uuid
from datetime import datetime
from pathlib import Path
from markitdown import MarkItDown
from resume_analysis.models import (
    UserProfile, JobDescription, SkillTaxonomy, ExtractedSkill, SkillGapReport, SkillGapDetail, Base
)
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

    # --- Load Skill Taxonomy from JSON ---
    taxonomy = load_taxonomy()
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

    # --- Create UserProfile and JobDescription from real data ---
    user = UserProfile(
        user_id=new_id(),
        name="",  # Optionally parse from resume_text
        email="", # Optionally parse from resume_text
        resume_text=resume_text,
        profile_url="",
        created_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()

    job = JobDescription(
        job_id=new_id(),
        title="",  # Optionally parse from job_text
        company="", # Optionally parse from job_text
        description_text=job_text,
        location="",
        created_at=datetime.utcnow()
    )
    session.add(job)
    session.commit()

    # --- Extract skills using LLM/NLP ---
    user_skills_raw = extract_skills(resume_text, taxonomy)
    job_skills_raw = extract_skills(job_text, taxonomy)

    # --- Insert ExtractedSkill entities ---
    extracted_skills = []
    for s in user_skills_raw:
        skill_id = taxonomy_map.get(s["skill"], new_id())
        extracted_skills.append(ExtractedSkill(
            extracted_id=new_id(),
            source_type="user_profile",
            source_id=user.user_id,
            skill_id=skill_id,
            raw_text=s.get("raw_text", s["skill"]),
            confidence=s.get("confidence", 1.0),
            proficiency=s.get("proficiency"),
            extracted_at=datetime.utcnow()
        ))
    for s in job_skills_raw:
        skill_id = taxonomy_map.get(s["skill"], new_id())
        extracted_skills.append(ExtractedSkill(
            extracted_id=new_id(),
            source_type="job_description",
            source_id=job.job_id,
            skill_id=skill_id,
            raw_text=s.get("raw_text", s["skill"]),
            confidence=s.get("confidence", 1.0),
            proficiency=s.get("proficiency"),
            extracted_at=datetime.utcnow()
        ))
    for s in extracted_skills:
        session.add(s)
    session.commit()

    # --- Skill Gap Analysis ---
    gap = skill_gap_analysis(user_skills_raw, job_skills_raw)
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
