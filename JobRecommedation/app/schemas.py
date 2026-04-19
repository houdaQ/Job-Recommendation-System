from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date

class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    skills_required: list[str]
    experience_years: int
    salary_range: Optional[str] = None
    job_type: str = "full-time"
    posted_date: Optional[date] = None

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: str
    model_config = {"from_attributes": True}

class CandidateProfile(BaseModel):
    name: str
    skills: list[str]
    experience_years: int
    desired_location: Optional[str] = None
    desired_job_type: Optional[str] = None
    bio: Optional[str] = None

    @field_validator("skills")
    @classmethod
    def skills_not_empty(cls, v):
        if not v:
            raise ValueError("skills list must not be empty")
        return [s.strip() for s in v if s.strip()]

class RecommendationItem(BaseModel):
    job: JobResponse
    score: float
    matching_skills: list[str]
    missing_skills: list[str]

class RecommendationResponse(BaseModel):
    candidate_name: str
    total_jobs_analyzed: int
    recommendations: list[RecommendationItem]

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None