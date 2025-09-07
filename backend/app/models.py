from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

class ScrapRequest(BaseModel):
    url: str