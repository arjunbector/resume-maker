from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

class JobQuestionsRequest(BaseModel):
    job_role: str
    company_name: str
    company_url: str
    job_description: str