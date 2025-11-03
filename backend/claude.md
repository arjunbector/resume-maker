# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-assisted resume builder backend built with FastAPI that helps users create personalized resumes by analyzing job descriptions and generating tailored questionnaires.

## Development Commands

### Running the Application

**Development mode (with hot reload):**
```bash
uv run app/main.py
```

**Docker deployment:**
```bash
# Build image
./run.sh build

# Build for AMD64
./run.sh build --amd

# Deploy locally
./run.sh deploy
```

### Package Management

**Install dependencies:**
```bash
uv sync
```

**Add a package:**
```bash
uv add <package-name>
```

## Environment Configuration

Required environment variables (create a `.env` file):
- `GEMINI_API_KEY` - API key for Gemini LLM integration
- `MONGODB_URI` - MongoDB connection string
- `SECRET_KEY` - Secret key for JWT token signing (change in production)

## Architecture

### Core Structure

The application follows a modular FastAPI architecture with clear separation of concerns:

**Entry Point:** [app/main.py](app/main.py)
- FastAPI app initialization with CORS middleware
- MongoDB connection lifecycle management via lifespan events
- Router registration for API endpoints
- Runs on port 8000 with uvicorn

### Key Components

**Database Layer** ([app/database/](app/database/))
- `client.py` - MongoDB singleton connection manager
- `models.py` - Pydantic models for data validation (User, Session, JobDetails, ResumeState, Questionnaire, KnowledgeGraph, ResumeStage, FieldMetadata, QuestionItem)
- `operations.py` - Database operations abstracted into UserOperations and SessionOperations classes

**API Routers** ([app/routers/](app/routers/))
- `auth.py` - Authentication endpoints (signup, login, logout, me at `/api/v1/auth`)
- `users.py` - User management endpoints (GET/PUT at `/api/v1/users`)
- `sessions.py` - Session management (POST/PUT at `/api/v1/sessions`)
- `ai.py` - AI endpoints for custom prompts and AI interactions (POST at `/api/v1/ai/custom`)

**AI Module** ([app/ai/](app/ai/))
- `agent.py` - ResumeAgent class for AI-powered resume generation and analysis (supports Gemini and Ollama via LiteLLM)
- `test_agent.py` - Test script for verifying agent functionality

**Services** ([app/services/](app/services/))
- `pipeline.py` - JobQuestionsPipeline for AI agent initialization with LiteLLM integration (supports Ollama and Gemini models)
- `scraper.py` - Web scraping tool for extracting job details from company URLs using BeautifulSoup

**Utilities** ([app/utils/](app/utils/))
- `auth.py` - Password hashing (bcrypt) and JWT token management
- `dependencies.py` - Reusable FastAPI dependencies for authentication (supports cookie and Authorization header)
- `prompt.py` - Prompt generation for AI models
- `questions.py` - Question parsing from AI responses

### Data Models

**User Model:**
- user_id (auto-generated UUID)
- email, hashed_password (bcrypt) - email is for authentication
- name, phone, resume_email, current_job_title, address (optional fields with defaults)
- resume_email - separate email to display on resume (optional, defaults to empty string)
- socials (dict for LinkedIn, etc.)
- knowledge_graph (KnowledgeGraph object with user's professional details)

**KnowledgeGraph Model:**
Structured storage for user's professional information:
- education (list of education records)
- work_experience (list of work history)
- research_work (list of research projects)
- projects (list of personal/professional projects)
- certifications (list of certifications)
- skills (list of skills)
- misc (dict for any additional information)

**JobDetails Model:**
- job_role, company_name, company_url, job_description (basic info)
- parsed_requirements (list of FieldMetadata - AI-extracted requirements)
- extracted_keywords (list of key skills/terms from job description)

**FieldMetadata Model:**
Metadata for job requirements and user profile fields:
- name (field name)
- type (field type, e.g., "skill", "work_experience")
- description (optional description)
- priority (1-5, importance level)
- confidence (0-1, AI confidence score)
- source ("ai_inferred" or "user_input")
- value (optional field value)

**ResumeState Model:**
Tracks the resume generation workflow:
- stage (ResumeStage enum: INIT, JOB_ANALYZED, REQUIREMENTS_IDENTIFIED, QUESTIONNAIRE_PENDING, READY_FOR_RESUME, COMPLETED, ERROR)
- required_fields (list of FieldMetadata - what's needed)
- missing_fields (list of FieldMetadata - what's still missing)
- ai_context (dict with AI analysis summary)
- last_action (string describing last operation)

**QuestionItem Model:**
Individual questionnaire question:
- id (unique question identifier)
- question (question text)
- related_field (which field this question gathers info for)
- answer (user's answer, optional)
- confidence (AI confidence in answer quality)
- status ("unanswered", "answered", "reviewed")

**Questionnaire Model:**
- questions (list of QuestionItem objects)
- completion (0.0-100.0 percentage of answered questions)

**Session Model:**
- session_id, user_id (UUIDs)
- resume_name, resume_description (optional fields for naming/describing the resume)
- job_details (JobDetails object with parsed requirements)
- resume_state (ResumeState tracking workflow stage)
- questionnaire (Questionnaire with context-aware questions)
- timestamps (last_active, created_at)

### Database Collections

- `users` - User profiles
- `sessions` - Resume building sessions with job context

### AI Pipeline

**ResumeAgent** ([app/ai/agent.py](app/ai/agent.py))
The main AI agent for resume generation and analysis:
- Supports multiple LLM providers (Gemini, Ollama)
- `run_prompt(prompt, system_prompt)` - Execute arbitrary prompts with optional system context
- `analyze_job_requirements(job_description)` - Extract requirements from job postings
- `compare_and_find_missing_fields(parsed_requirements, user_knowledge_graph)` - Identify gaps in user profile
- `generate_questionnaire(missing_fields)` - Create short, targeted questions for missing information
- `process_answer(question, answer, related_field, field_type)` - Extract structured data from user answers
- Automatic model initialization based on provider string
- Built on LiteLLMModel for flexible provider support

**JobQuestionsPipeline** (Legacy - [app/services/pipeline.py](app/services/pipeline.py))
Uses smolagents framework with:
- LiteLLMModel for flexible LLM provider support (Gemini/Ollama)
- ToolCallingAgent with web scraping capabilities
- get_website_content tool for fetching job posting details

**Testing the Agent:**
```bash
uv run app/ai/test_agent.py
```

## API Patterns

### Authentication
The application uses JWT-based authentication with flexible token delivery:
- Users sign up with email/password (POST `/api/v1/auth/signup`)
- Login returns access_token in response body AND sets httpOnly cookie (30 day expiry)
- Token contains user_id (sub) and email
- Authentication supports both:
  1. Cookie-based: `access_token` cookie (checked first)
  2. Header-based: `Authorization: Bearer {token}` header (fallback)
- `/api/v1/auth/me` retrieves current user from token
- Logout removes the cookie

**For Protected Routes:**
Use the `get_current_user` dependency from `utils.dependencies`:
```python
from fastapi import Depends
from utils.dependencies import get_current_user

@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    # current_user contains user data without hashed_password
    return {"message": f"Hello {current_user['email']}"}
```

### Error Handling
All endpoints follow consistent error handling:
- ValueError → 400/404 status codes
- 401 for authentication failures
- Generic exceptions → 500 with error details
- Logging via loguru for all operations

### Database Operations
- All DB operations check for entity existence before modifications
- UUIDs auto-generated for user_id and session_id when not provided
- Passwords are hashed with bcrypt before storage (never store plain passwords)
- Timestamps automatically managed (last_active updated on session changes)
- Protected fields (user_id, email, session_id, hashed_password) cannot be updated
- User creation via auth endpoints only (signup with email/password)

### Router Organization
- Routers use APIRouter with prefixes and tags
- Query parameters for entity lookup (email, user_id, session_id)
- Request bodies for creation/update data
- Consistent response format: `{message, ...entity_data}`

## Important Implementation Notes

### Application Startup
The application uses FastAPI's lifespan context manager for resource initialization and cleanup:

**On Startup:**
- MongoDB connection is established via `mongodb.connect()`
- AI agent (ResumeAgent) is initialized and stored in `app.state.agent` with the configured model (default: `gemini/gemini-2.5-flash`)
- Agent is accessible from any router via `request.app.state.agent`

**On Shutdown:**
- MongoDB connection is closed via `mongodb.close()`

**Example lifespan implementation:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    mongodb.connect()
    app.state.agent = ResumeAgent(model="gemini/gemini-2.5-flash")
    logger.info("AI agent initialized")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    mongodb.close()

app = FastAPI(lifespan=lifespan)
```

**Using the AI agent in routers:**
```python
@router.post("/custom")
def run_custom_prompt(request: CustomPromptRequest, app_request: Request):
    agent = app_request.app.state.agent
    response = agent.run_prompt(prompt=request.prompt)
    return {"response": response}
```

### Other Notes
- **CORS middleware must be added BEFORE routers** in main.py for proper functionality
- CORS is configured to allow all origins for development with credentials support
- JWT tokens use HS256 algorithm with SECRET_KEY from environment
- Cookies are httpOnly for security (prevents XSS attacks)
- Cookie settings use `samesite="none"` and `secure=True` for cross-origin requests
- The job-questions endpoint is currently commented out in main.py but the pipeline infrastructure remains in place
- Web scraper limits content (10 headings, 15 paragraphs, 5000 chars) to manage response size
- Session operations automatically update last_active timestamp
- Most user and session endpoints now use authentication and don't require manual user_id/email parameters

## Security Considerations

- Passwords are hashed using bcrypt (native bcrypt library, not passlib)
- JWT tokens stored in httpOnly cookies to prevent XSS
- Token also returned in response body for clients that need header-based auth
- Token expiry set to 30 days
- Authentication dependency checks cookie first, then Authorization header
- Cookie settings: `samesite="none"`, `secure=True` (required for cross-origin requests)
- SECRET_KEY should be a strong random value in production
- Frontend must include `credentials: 'include'` (fetch) or `withCredentials: true` (axios)
- Consider adding rate limiting for auth endpoints in production