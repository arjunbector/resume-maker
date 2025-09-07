from fastapi import FastAPI
from models import PromptRequest, ScrapRequest
from services.smolagents_pipeline import pipeline
from services.scraper import scraper
import uvicorn

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

@app.post("/scrape")
def scrape_website(request: ScrapRequest):
    result = scraper.scrape_website(request.url)
    print(f"Scraped content from {request.url}:")
    print(result)
    return result

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)