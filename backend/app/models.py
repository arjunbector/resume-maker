from pydantic import BaseModel
from typing import Optional

class PromptRequest(BaseModel):
    prompt: str

class ScrapRequest(BaseModel):
    url: str

class SummaryRequest(BaseModel):
    url: str
    summary_type: Optional[str] = "general"

class JobQuestionsRequest(BaseModel):
    job_role: str
    company_url: str
    job_description: str