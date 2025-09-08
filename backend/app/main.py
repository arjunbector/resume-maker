from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from models import PromptRequest, ScrapRequest, SummaryRequest, JobQuestionsRequest
from services.smolagents_pipeline import pipeline
from services.scraper import scraper
from services.website_summary_pipeline import website_summary_pipeline
from services.job_questions_pipeline import job_questions_pipeline
import uvicorn

app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/job-questions")
def generate_job_questions(request: JobQuestionsRequest):
    result = job_questions_pipeline.generate_questions(
        request.job_role, 
        request.company_url, 
        request.job_description
    )
    company_name = result.get('company_name', request.company_url)
    print(f"Generated {result.get('total_questions', 0)} questions for {request.job_role} at {company_name}:")
    if 'questions' in result and result['success']:
        for i, question in enumerate(result['questions'], 1):
            print(f"{i}. {question}")
        return {
            "questions": result['questions'],
            "total_questions": result.get('total_questions', 0),
            "job_role": result.get('job_role'),
            "company_name": result.get('company_name')
        }
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return {"error": result.get('error', 'Unknown error')}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)