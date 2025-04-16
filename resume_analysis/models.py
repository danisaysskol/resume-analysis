import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Enum, ForeignKey, DateTime, create_engine
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON

Base = declarative_base()

def gen_uuid():
    return str(uuid.uuid4())

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    user_id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    resume_text = Column(Text, nullable=False)
    profile_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    skill_gap_reports = relationship('SkillGapReport', back_populates='user_profile')

class JobDescription(Base):
    __tablename__ = 'job_descriptions'
    job_id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description_text = Column(Text, nullable=False)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    skill_gap_reports = relationship('SkillGapReport', back_populates='job_description')

class SkillTaxonomy(Base):
    __tablename__ = 'skill_taxonomy'
    skill_id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    category = Column(String)
    description = Column(Text)
    related_skills = Column(SQLITE_JSON)  # List of skill_ids
    source = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)
    extracted_skills = relationship('ExtractedSkill', back_populates='skill')
    gap_details = relationship('SkillGapDetail', back_populates='skill')

class ExtractedSkill(Base):
    __tablename__ = 'extracted_skills'
    extracted_id = Column(String, primary_key=True, default=gen_uuid)
    source_type = Column(Enum('user_profile', 'job_description'), nullable=False)
    source_id = Column(String, nullable=False)
    skill_id = Column(String, ForeignKey('skill_taxonomy.skill_id'), nullable=False)
    raw_text = Column(String)
    confidence = Column(Float)
    proficiency = Column(String)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    skill = relationship('SkillTaxonomy', back_populates='extracted_skills')

class SkillGapReport(Base):
    __tablename__ = 'skill_gap_reports'
    report_id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey('user_profiles.user_id'), nullable=False)
    job_id = Column(String, ForeignKey('job_descriptions.job_id'), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    match_score = Column(Float)
    summary = Column(Text)
    user_profile = relationship('UserProfile', back_populates='skill_gap_reports')
    job_description = relationship('JobDescription', back_populates='skill_gap_reports')
    details = relationship('SkillGapDetail', back_populates='report')

class SkillGapDetail(Base):
    __tablename__ = 'skill_gap_details'
    detail_id = Column(String, primary_key=True, default=gen_uuid)
    report_id = Column(String, ForeignKey('skill_gap_reports.report_id'), nullable=False)
    skill_id = Column(String, ForeignKey('skill_taxonomy.skill_id'), nullable=False)
    status = Column(Enum('Matched', 'Missing', 'Transferable', 'Low Proficiency'), nullable=False)
    user_proficiency = Column(String)
    job_proficiency = Column(String)
    similarity_score = Column(Float)
    notes = Column(Text)
    report = relationship('SkillGapReport', back_populates='details')
    skill = relationship('SkillTaxonomy', back_populates='gap_details')
