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
- `models.py` - Pydantic models for data validation (User, Session, JobDetails, ResumeState, Questionnaire)
- `operations.py` - Database operations abstracted into UserOperations and SessionOperations classes

**API Routers** ([app/routers/](app/routers/))
- `auth.py` - Authentication endpoints (signup, login, logout, me at `/api/v1/auth`)
- `users.py` - User management endpoints (GET/PUT at `/api/v1/users`)
- `sessions.py` - Session management (POST/PUT at `/api/v1/sessions`)

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
- email, hashed_password (bcrypt)
- name, phone, address (optional fields with defaults)
- socials (dict for LinkedIn, etc.)

**Session Model:**
- session_id, user_id (UUIDs)
- job_details (role, company, URL, description)
- resume_state (status, missing_fields)
- questionnaire (questions list, answers dict)
- timestamps (last_active, created_at)

### Database Collections

- `users` - User profiles
- `sessions` - Resume building sessions with job context

### AI Pipeline

The JobQuestionsPipeline uses smolagents framework with:
- LiteLLMModel for flexible LLM provider support (Gemini/Ollama)
- ToolCallingAgent with web scraping capabilities
- get_website_content tool for fetching job posting details

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

- MongoDB connection is established on app startup and closed on shutdown via lifespan context manager
- CORS is configured to allow all origins for development
- JWT tokens use HS256 algorithm with SECRET_KEY from environment
- Cookies are httpOnly for security (prevents XSS attacks)
- In production, set cookie `secure=True` to require HTTPS
- The job-questions endpoint is currently commented out in main.py but the pipeline infrastructure remains in place
- Web scraper limits content (10 headings, 15 paragraphs, 5000 chars) to manage response size
- Session operations automatically update last_active timestamp

## Security Considerations

- Passwords are hashed using bcrypt (native bcrypt library, not passlib)
- JWT tokens stored in httpOnly cookies to prevent XSS
- Token also returned in response body for clients that need header-based auth
- Token expiry set to 30 days
- Authentication dependency checks cookie first, then Authorization header
- SECRET_KEY should be a strong random value in production
- Consider adding rate limiting for auth endpoints in production
- Cookie `secure` flag should be True when using HTTPS