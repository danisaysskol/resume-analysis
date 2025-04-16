import uuid
from datetime import datetime
from resume_analysis.models import (
    UserProfile, JobDescription, SkillTaxonomy, ExtractedSkill, SkillGapReport, SkillGapDetail, Base
)
from resume_analysis.db_utils import create_all_tables, SessionLocal, export_table_to_json

# --- Helper for UUIDs ---
def new_id():
    return str(uuid.uuid4())

def seed_and_export():
    create_all_tables()
    session = SessionLocal()

    # --- Seed SkillTaxonomy ---
    skills = [
        SkillTaxonomy(skill_id=new_id(), name="Python", category="Programming", description="Programming language", source="Custom"),
        SkillTaxonomy(skill_id=new_id(), name="Communication", category="Soft Skill", description="Oral and written communication", source="Custom"),
        SkillTaxonomy(skill_id=new_id(), name="Project Management", category="Management", description="Managing projects", source="Custom"),
    ]
    for s in skills:
        session.add(s)
    session.commit()

    # --- Seed UserProfile ---
    user = UserProfile(
        user_id=new_id(),
        name="Ali Khan",
        email="ali.khan@email.com",
        resume_text="Experienced Python developer with strong communication and project management skills.",
        profile_url="https://linkedin.com/in/alikhan",
        created_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()

    # --- Seed JobDescription ---
    job = JobDescription(
        job_id=new_id(),
        title="Backend Engineer",
        company="PakTech Solutions",
        description_text="Looking for a Python backend engineer with project management experience and excellent communication skills.",
        location="Lahore, Pakistan",
        created_at=datetime.utcnow()
    )
    session.add(job)
    session.commit()

    # --- Map skill names to skill_ids ---
    skill_map = {s.name: s.skill_id for s in session.query(SkillTaxonomy).all()}

    # --- Seed ExtractedSkill for user and job ---
    user_skills = [
        ExtractedSkill(
            extracted_id=new_id(),
            source_type="user_profile",
            source_id=user.user_id,
            skill_id=skill_map["Python"],
            raw_text="Python",
            confidence=0.98,
            proficiency="Expert",
            extracted_at=datetime.utcnow()
        ),
        ExtractedSkill(
            extracted_id=new_id(),
            source_type="user_profile",
            source_id=user.user_id,
            skill_id=skill_map["Communication"],
            raw_text="communication",
            confidence=0.95,
            proficiency="Advanced",
            extracted_at=datetime.utcnow()
        ),
    ]
    job_skills = [
        ExtractedSkill(
            extracted_id=new_id(),
            source_type="job_description",
            source_id=job.job_id,
            skill_id=skill_map["Python"],
            raw_text="Python",
            confidence=0.99,
            proficiency="Required",
            extracted_at=datetime.utcnow()
        ),
        ExtractedSkill(
            extracted_id=new_id(),
            source_type="job_description",
            source_id=job.job_id,
            skill_id=skill_map["Project Management"],
            raw_text="project management",
            confidence=0.96,
            proficiency="Required",
            extracted_at=datetime.utcnow()
        ),
    ]
    for s in user_skills + job_skills:
        session.add(s)
    session.commit()

    # --- Seed SkillGapReport ---
    report = SkillGapReport(
        report_id=new_id(),
        user_id=user.user_id,
        job_id=job.job_id,
        generated_at=datetime.utcnow(),
        match_score=85.0,
        summary="User matches Python and communication, missing project management."
    )
    session.add(report)
    session.commit()

    # --- Seed SkillGapDetail ---
    gap_details = [
        SkillGapDetail(
            detail_id=new_id(),
            report_id=report.report_id,
            skill_id=skill_map["Python"],
            status="Matched",
            user_proficiency="Expert",
            job_proficiency="Required",
            similarity_score=1.0,
            notes="User is expert in Python as required."
        ),
        SkillGapDetail(
            detail_id=new_id(),
            report_id=report.report_id,
            skill_id=skill_map["Project Management"],
            status="Missing",
            user_proficiency=None,
            job_proficiency="Required",
            similarity_score=0.0,
            notes="User does not mention project management."
        ),
    ]
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
