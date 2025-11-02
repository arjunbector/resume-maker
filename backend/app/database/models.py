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

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class KnowledgeGraph(BaseModel):
    education: List[Dict] = []
    work_experience: List[Dict] = []
    research_work: List[Dict] = []
    projects: List[Dict] = []
    certifications: List[Dict] = []
    skills: List[str] = []
    misc: Dict = {}

class User(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = ""
    email: str
    hashed_password: str
    phone: Optional[str] = ""
    socials: Optional[Dict[str, str]] = {}
    address: Optional[str] = ""
    knowledge_graph: Optional[KnowledgeGraph] = KnowledgeGraph()

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    phone: str
    socials: Dict[str, str]
    address: str
    knowledge_graph: KnowledgeGraph

class Session(BaseModel):
    session_id: str
    user_id: str
    job_details: JobDetails
    resume_state: ResumeState
    questionnaire: Questionnaire
    last_active: datetime
    created_at: datetime
