from fastapi import FastAPI
from services.smolagents_pipeline import pipeline
import uvicorn

from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

app = FastAPI()

@app.get("/")
def root():
    response = pipeline.process_prompt(
        "Give me a cheeky one line ping message for my API. Only give me the message, no other text."
    )
    return {"message": f"{response}"}

@app.post("/process")
def process_prompt(request: PromptRequest):
    response = pipeline.process_prompt(request.prompt)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)