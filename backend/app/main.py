from fastapi import FastAPI
from models import PromptRequest, ScrapRequest, SummaryRequest
from services.smolagents_pipeline import pipeline
from services.scraper import scraper
from services.website_summary_pipeline import website_summary_pipeline
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

@app.post("/summarize")
def summarize_website(request: SummaryRequest):
    result = website_summary_pipeline.summarize_website(request.url, request.summary_type)
    print(f"Generated {request.summary_type} summary for {request.url}:")
    print(result)
    if 'ai_summary' in result:
        print(result['ai_summary'])
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    return result["ai_summary"]

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)