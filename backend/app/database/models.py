from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class PromptRequest(BaseModel):
    prompt: str

class ResumeStage(str, Enum):
    INIT = "init"
    JOB_ANALYZED = "job_analyzed"
    REQUIREMENTS_IDENTIFIED = "requirements_identified"
    QUESTIONNAIRE_PENDING = "questionnaire_pending"
    READY_FOR_RESUME = "ready_for_resume"
    COMPLETED = "completed"
    ERROR = "error"

class FieldMetadata(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = 1
    confidence: Optional[float] = None
    source: Optional[str] = "ai_inferred"  # or "user_input"
    value: Optional[str] = None

class JobDetails(BaseModel):
    job_role: str
    company_name: str
    company_url: str
    job_description: str
    parsed_requirements: Optional[List[FieldMetadata]] = []
    extracted_keywords: Optional[List[str]] = []

# Alias for backward compatibility
JobQuestionsRequest = JobDetails

class ResumeState(BaseModel):
    stage: ResumeStage = ResumeStage.INIT
    required_fields: List[FieldMetadata] = []
    missing_fields: List[FieldMetadata] = []
    ai_context: Optional[Dict] = {}  # summary snapshot from last AI call
    last_action: Optional[str] = None

class QuestionItem(BaseModel):
    id: str
    question: str
    related_field: str
    answer: Optional[str] = None
    confidence: Optional[float] = None
    status: str = "unanswered"  # or "answered", "reviewed"

class Questionnaire(BaseModel):
    questions: List[QuestionItem] = []
    completion: float = 0.0  # percentage of answered questions

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
    current_job_title: Optional[str] = ""
    socials: Optional[Dict[str, str]] = {}
    address: Optional[str] = ""
    knowledge_graph: Optional[KnowledgeGraph] = KnowledgeGraph()

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    phone: str
    current_job_title: str
    socials: Dict[str, str]
    address: str
    knowledge_graph: KnowledgeGraph

class Session(BaseModel):
    session_id: str
    user_id: str
    resume_name: Optional[str] = ""
    resume_description: Optional[str] = ""
    job_details: JobDetails
    resume_state: ResumeState
    questionnaire: Questionnaire
    last_active: datetime
    created_at: datetime
