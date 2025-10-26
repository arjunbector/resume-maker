from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class PromptRequest(BaseModel):
    prompt: str

class JobQuestionsRequest(BaseModel):
    job_role: str
    company_name: str
    company_url: str
    job_description: str

class ResumeState(BaseModel):
    status: str
    missing_fields: List[str]

class Questionnaire(BaseModel):
    questions: List[str]
    answers: Dict[str, str]

class User(BaseModel):
    user_id: str
    name: str
    email: str
    phone: str
    socials: Dict[str, str]
    address: str

class Session(BaseModel):
    session_id: str
    user_id: str
    job_details: Dict
    resume_state: ResumeState
    questionnaire: Questionnaire
    last_active: datetime
    created_at: datetime
