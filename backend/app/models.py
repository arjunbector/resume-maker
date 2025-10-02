from pydantic import BaseModel
from typing import Optional

class PromptRequest(BaseModel):
    prompt: str

class JobQuestionsRequest(BaseModel):
    job_role: str
    company_url: str
    job_description: str