from pydantic import BaseModel
from typing import List, Optional

class ExtractedSkillModel(BaseModel):
    skill: str
    proficiency: Optional[str] = None
    confidence: Optional[float] = None
    raw_text: Optional[str] = None

class UserProfileModel(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    resume_text: str

class JobDescriptionModel(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description_text: str
    location: Optional[str] = None

class ExtractedSkillsList(BaseModel):
    skills: List[ExtractedSkillModel]
