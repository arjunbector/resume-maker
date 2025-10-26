from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class PromptRequest(BaseModel):
    prompt: str

class JobDetails(BaseModel):
    job_role: str
    company_name: str
    company_url: str
    job_description: str

# Alias for backward compatibility
JobQuestionsRequest = JobDetails

class ResumeState(BaseModel):
    status: str
    missing_fields: List[str]

class Questionnaire(BaseModel):
    questions: List[str]
    answers: Dict[str, str]

class User(BaseModel):
    user_id: Optional[str] = None
    name: str
    email: str
    phone: str
    socials: Dict[str, str]
    address: str

class Session(BaseModel):
    session_id: str
    user_id: str
    job_details: JobDetails
    resume_state: ResumeState
    questionnaire: Questionnaire
    last_active: datetime
    created_at: datetime
