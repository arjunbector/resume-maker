from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from models import PromptRequest, JobQuestionsRequest
from services.pipeline import JobQuestionsPipeline
from utils.prompt import generate_prompt
from utils.questions import parse_questions
import uvicorn

app = FastAPI()

pipeline = JobQuestionsPipeline(model="gemini/gemini-2.5-flash")

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
    return {"message": "Ping Pong!"}

@app.post("/job-questions")
def generate_job_questions(request: JobQuestionsRequest):
    try:
        # Generate the prompt from the request
        prompt = generate_prompt(request)

        # Run the agent with the tool
        result = pipeline.agent.run(prompt)

        # Parse questions from the result
        questions = parse_questions(result)

        # Log for debugging
        print("ToolCallingAgent:", result)
        print("Questions:", questions)

        # Validate that we have questions
        if not questions or len(questions) == 0:
            return {
                "error": "No questions could be generated from the response",
                "raw_response": result
            }

        return {
            "questions": questions,
            "total_questions": len(questions),
            "job_role": request.job_role,
            "company_url": request.company_url
        }

    except Exception as e:
        print(f"Error in job-questions endpoint: {str(e)}")
        return {
            "error": f"Failed to generate questions: {str(e)}",
            "job_role": request.job_role,
            "company_url": request.company_url
        }

    

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)