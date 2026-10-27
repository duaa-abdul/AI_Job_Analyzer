from typing import List
from pydantic import BaseModel, Field


class JobInformation(BaseModel):
    job_title: str = "Not specified"
    company_name: str = "Not specified"
    required_experience: str = "Not specified"
    required_skills: List[str] = Field(default_factory=list)


class JobClassification(BaseModel):
    job_category: str = "Other"
    employment_type: str = "Not specified"
    work_arrangement: str = "Not specified"


class SkillAnalysis(BaseModel):
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    top_3_skills: List[str] = Field(default_factory=list)


class HiringReport(BaseModel):
    job_title: str
    company_name: str
    required_experience: str
    required_skills: List[str]
    job_category: str
    employment_type: str
    work_arrangement: str
    technical_skills: List[str]
    soft_skills: List[str]
    top_3_skills: List[str]
    hiring_summary: str
