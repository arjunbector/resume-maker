from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from database.models import JobQuestionsRequest
from database.client import mongodb
from services.pipeline import JobQuestionsPipeline
from utils.prompt import generate_prompt
from utils.questions import parse_questions
from routers import users, sessions
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb.connect()
    yield
    mongodb.close()

app = FastAPI(lifespan=lifespan)

pipeline = JobQuestionsPipeline(model="gemini/gemini-2.5-flash")

# Include routers
app.include_router(users.router)
app.include_router(sessions.router)

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

@app.post("/api/v1/job-questions")
def generate_job_questions(request: JobQuestionsRequest):
    try:
        logger.info(f"Generating job questions for role: {request.job_role} at {request.company_name}")

        # Generate the prompt from the request
        prompt = generate_prompt(request)

        # Run the agent with the tool
        result = pipeline.agent.run(prompt)

        # Parse questions from the result
        questions = parse_questions(result)

        logger.debug(f"ToolCallingAgent result: {result}")
        logger.info(f"Generated {len(questions)} questions")

        # Validate that we have questions
        if not questions or len(questions) == 0:
            logger.warning("No questions could be generated from the response")
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
        logger.error(f"Error in job-questions endpoint: {str(e)}")
        return {
            "error": f"Failed to generate questions: {str(e)}",
            "job_role": request.job_role,
            "company_url": request.company_url
        }

    

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)