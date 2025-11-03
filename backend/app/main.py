from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from database.models import JobQuestionsRequest
from database.client import mongodb
from services.pipeline import JobQuestionsPipeline
from ai.agent import ResumeAgent
from utils.prompt import generate_prompt
from utils.questions import parse_questions
from routers import users, sessions, auth, ai
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize connections and agents
    logger.info("Starting up application...")
    mongodb.connect()

    # Initialize AI agent
    app.state.agent = ResumeAgent(model="gemini/gemini-2.5-flash")
    logger.info("AI agent initialized")

    yield

    # Shutdown: Clean up resources
    logger.info("Shutting down application...")
    mongodb.close()

app = FastAPI(lifespan=lifespan)

pipeline = JobQuestionsPipeline(model="gemini/gemini-2.5-flash")

# Add CORS middleware BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(sessions.router)
app.include_router(ai.router)

@app.get("/")
def root():
    return {"message": "Ping Pong!"}
    

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)