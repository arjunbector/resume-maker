# API Documentation

## Base URL
`http://localhost:8000`

## Authentication

All protected endpoints support two authentication methods:
1. **Cookie-based:** `access_token` cookie (set automatically on login/signup)
2. **Header-based:** `Authorization: Bearer {token}` header

The server checks for the token in cookies first, then falls back to the Authorization header.

## Endpoints

### Authentication

#### Sign Up
**POST** `/api/v1/auth/signup`

Create a new user account with email and password. Sets JWT access token in cookie.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "user_id": "string",
  "email": "string",
  "access_token": "string"
}
```

**Cookie Set:**
- `access_token` - JWT token (httpOnly, 30 days expiry)

*Note: The `access_token` is returned in both the response body (for header-based auth) and as a cookie (for cookie-based auth).*

**Status Codes:**
- `200` - User created successfully
- `400` - User already exists
- `500` - Server error

#### Login
**POST** `/api/v1/auth/login`

Login with email and password. Sets JWT access token in cookie.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user_id": "string",
  "email": "string",
  "access_token": "string"
}
```

**Cookie Set:**
- `access_token` - JWT token (httpOnly, 30 days expiry)

*Note: The `access_token` is returned in both the response body (for header-based auth) and as a cookie (for cookie-based auth).*

**Status Codes:**
- `200` - Login successful
- `401` - Invalid email or password
- `500` - Server error

#### Get Current User
**GET** `/api/v1/auth/me`

Get current authenticated user details from JWT token.
Supports both cookie-based and header-based authentication.

**Authentication (choose one):**
1. **Cookie:** `access_token` - JWT token from login/signup
2. **Header:** `Authorization: Bearer {token}` - JWT token

*Note: Cookie authentication is tried first, then Authorization header.*

**Response:**
```json
{
  "user_id": "string",
  "name": "string",
  "email": "string",
  "phone": "string",
  "socials": {
    "linkedin": "string"
  },
  "address": "string",
  "knowledge_graph": {
    "education": [],
    "work_experience": [],
    "research_work": [],
    "projects": [],
    "certifications": [],
    "skills": [],
    "misc": {}
  }
}
```

**Status Codes:**
- `200` - User details retrieved
- `401` - Not authenticated or invalid token
- `404` - User not found
- `500` - Server error

#### Logout
**POST** `/api/v1/auth/logout`

Logout user by removing the access token cookie.

**Response:**
```json
{
  "message": "Logout successful"
}
```

**Status Codes:**
- `200` - Logout successful
- `500` - Server error

---

### Users

#### Get User
**GET** `/api/v1/users`

Get user by email.

**Query Parameters:**
- `email` (required) - User's email address

**Response:**
```json
{
  "user_id": "string",
  "name": "string",
  "email": "string",
  "phone": "string",
  "socials": {
    "linkedin": "string"
  },
  "address": "string",
  "knowledge_graph": {
    "education": [],
    "work_experience": [],
    "research_work": [],
    "projects": [],
    "certifications": [],
    "skills": [],
    "misc": {}
  }
}
```

**Status Codes:**
- `200` - User found
- `404` - User not found
- `500` - Server error

#### Update User
**PUT** `/api/v1/users`

Update user fields by email.

**Query Parameters:**
- `email` (required) - User's email address

**Request Body:**
```json
{
  "name": "string",
  "phone": "string",
  "socials": {
    "linkedin": "string"
  },
  "address": "string",
  "knowledge_graph": {
    "education": [
      {
        "institution": "string",
        "degree": "string",
        "field": "string",
        "start_date": "string",
        "end_date": "string",
        "gpa": "string"
      }
    ],
    "work_experience": [
      {
        "company": "string",
        "position": "string",
        "start_date": "string",
        "end_date": "string",
        "description": "string"
      }
    ],
    "research_work": [],
    "projects": [],
    "certifications": [],
    "skills": ["Python", "JavaScript"],
    "misc": {}
  }
}
```

*Note: `email`, `user_id`, and `hashed_password` cannot be updated. All fields are optional.*

**Response:**
```json
{
  "message": "User updated successfully",
  "email": "string",
  "modified_count": 1
}
```

**Status Codes:**
- `200` - User updated successfully
- `404` - User not found
- `500` - Server error

---

### AI

#### Run Custom Prompt
**POST** `/api/v1/ai/custom`

Execute a custom prompt through the AI agent. Useful for testing, experimentation, or custom AI interactions.

**Request Body:**
```json
{
  "prompt": "string",
  "system_prompt": "string (optional)",
  "model": "string (optional)"
}
```

**Model Options:**
- `gemini/gemini-2.5-flash` (default)
- `ollama_chat/gpt-oss` (requires Ollama running locally)

**Example Request:**
```json
{
  "prompt": "What are the top 5 skills for a software engineer?",
  "system_prompt": "You are a helpful resume writing assistant.",
  "model": "gemini/gemini-2.5-flash"
}
```

**Response:**
```json
{
  "response": "string",
  "model": "gemini/gemini-2.5-flash",
  "prompt_length": 50,
  "response_length": 200
}
```

**Status Codes:**
- `200` - Prompt executed successfully
- `500` - Server error

#### Analyze Job Requirements
**POST** `/api/v1/ai/analyze`

Analyze a job description and extract all requirements, qualifications, and keywords. This endpoint does NOT compare against the user's profile - it purely extracts information from the job posting.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "job_description": "string (required)",
  "job_role": "string (optional)",
  "company_name": "string (optional)",
  "session_id": "string (optional)"
}
```

**Example Request:**
```json
{
  "job_description": "We are looking for a Senior Backend Engineer with 5+ years experience in Python, FastAPI, and MongoDB. Strong knowledge of REST APIs and microservices architecture required. Experience with Docker and Kubernetes is a plus.",
  "job_role": "Senior Backend Engineer",
  "company_name": "Tech Corp",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Note:** If `session_id` is provided, the endpoint will automatically update the session with:
- Parsed requirements in `job_details.parsed_requirements`
- Extracted keywords in `job_details.extracted_keywords`
- Resume state updated to `JOB_ANALYZED` stage
- Required fields populated in `resume_state`

**Response:**
```json
{
  "message": "Job analysis completed",
  "user_id": "string",
  "job_role": "Senior Backend Engineer",
  "company_name": "Tech Corp",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_updated": true,
  "analysis": {
    "parsed_requirements": [
      {
        "name": "Python",
        "type": "skill",
        "description": "5+ years experience in Python programming",
        "priority": 5,
        "confidence": 0.95
      },
      {
        "name": "FastAPI",
        "type": "skill",
        "description": "Backend web framework",
        "priority": 5,
        "confidence": 0.95
      },
      {
        "name": "MongoDB",
        "type": "skill",
        "description": "NoSQL database",
        "priority": 5,
        "confidence": 0.95
      },
      {
        "name": "REST APIs",
        "type": "experience",
        "description": "Strong knowledge of REST APIs",
        "priority": 5,
        "confidence": 0.9
      },
      {
        "name": "Microservices",
        "type": "experience",
        "description": "Microservices architecture",
        "priority": 5,
        "confidence": 0.9
      },
      {
        "name": "Docker",
        "type": "skill",
        "description": "Containerization (nice to have)",
        "priority": 3,
        "confidence": 0.7
      },
      {
        "name": "Kubernetes",
        "type": "skill",
        "description": "Container orchestration (nice to have)",
        "priority": 3,
        "confidence": 0.7
      }
    ],
    "extracted_keywords": ["Python", "FastAPI", "MongoDB", "REST APIs", "microservices", "Docker", "Kubernetes", "Backend Engineer", "5+ years"]
  },
  "parsed_requirements": [...],
  "extracted_keywords": [...]
}
```

**Response Fields:**
- `session_updated`: Boolean indicating whether the session was successfully updated (only present if `session_id` was provided)

**Field Descriptions:**
- `parsed_requirements`: Detailed list of specific requirements extracted from the job description
  - `priority` (1-5): 5=critical/required, 4=strongly preferred, 3=preferred, 2=mentioned, 1=tangentially related
  - `confidence` (0.0-1.0): How explicitly the requirement is stated in the job description
  - `type`: Category (skill, education, certification, experience, project)
- `extracted_keywords`: Important keywords, technologies, and phrases mentioned in the job posting

**Status Codes:**
- `200` - Analysis completed successfully
- `401` - Not authenticated or invalid token
- `500` - Server error

---

#### Compare with User Profile
**POST** `/api/v1/ai/compare`

Compare job requirements from an analyzed session with the user's knowledge graph to identify missing and matched fields.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Query Parameters:**
- `session_id` (required) - Session ID with analyzed job requirements

**Example Request:**
```
POST /api/v1/ai/compare?session_id=550e8400-e29b-41d4-a716-446655440000
```

**Prerequisites:**
- Session must exist and belong to the authenticated user
- Session must have been analyzed first using `/api/v1/ai/analyze` (must have `parsed_requirements`)

**Response:**
```json
{
  "message": "Requirements comparison completed",
  "user_id": "user-uuid-here",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "missing_fields": [
    {
      "name": "Docker",
      "type": "skill",
      "description": "User does not have Docker experience in profile",
      "priority": 5,
      "confidence": 0.9,
      "source": "ai_inferred"
    },
    {
      "name": "Kubernetes",
      "type": "skill",
      "description": "No Kubernetes experience found",
      "priority": 3,
      "confidence": 0.85,
      "source": "ai_inferred"
    }
  ],
  "matched_fields": [
    {
      "name": "Python",
      "type": "skill",
      "description": "User has 6 years of Python experience",
      "priority": 5,
      "confidence": 0.95,
      "source": "user_knowledge_graph",
      "value": "Python - 6 years"
    },
    {
      "name": "FastAPI",
      "type": "skill",
      "description": "User has FastAPI projects in profile",
      "priority": 5,
      "confidence": 0.9,
      "source": "user_knowledge_graph",
      "value": "FastAPI projects: Resume Builder, API Gateway"
    }
  ],
  "fill_suggestions": [
    {
      "field_name": "Docker",
      "suggestion": "Add Docker containerization to your recent projects or create a demo project using Docker",
      "category": "skill"
    },
    {
      "field_name": "Kubernetes",
      "suggestion": "Consider adding a certification or project that demonstrates Kubernetes orchestration",
      "category": "skill"
    }
  ],
  "total_missing": 2,
  "total_matched": 8
}
```

**What This Endpoint Does:**
1. Retrieves the session and verifies ownership
2. Compares each job requirement against the user's knowledge graph (education, experience, skills, projects, certifications)
3. Identifies which requirements are missing from the user's profile
4. Identifies which requirements the user already satisfies
5. Provides actionable suggestions for filling missing fields
6. Updates the session's `resume_state.missing_fields` and advances stage to `REQUIREMENTS_IDENTIFIED`

**Session Updates:**
The endpoint automatically updates the session with:
- `resume_state.missing_fields`: List of requirements not found in user's profile
- `resume_state.stage`: Set to `REQUIREMENTS_IDENTIFIED`
- `resume_state.ai_context`: Summary with comparison statistics and fill suggestions
- `resume_state.last_action`: Set to `requirements_compared`

**Status Codes:**
- `200` - Comparison completed successfully
- `400` - Session has no parsed requirements (need to analyze first)
- `401` - Not authenticated or invalid token
- `403` - Session does not belong to authenticated user
- `404` - Session not found
- `500` - Server error

---

### Sessions

#### Create Session
**POST** `/api/v1/sessions`

Create a new blank session for the authenticated user. The session is created with empty job details that can be populated later using the update endpoint or the `/api/v1/ai/analyze` endpoint.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Request Body:**
None (empty)

**Response:**
```json
{
  "message": "Session created successfully",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-uuid-here"
}
```

**Notes:**
- Session is created with blank job details (empty strings and empty arrays)
- Initial stage is set to `INIT`
- Use the session_id with `/api/v1/ai/analyze` to populate job details
- Or use `/api/v1/sessions` PUT endpoint to manually update session data

**Status Codes:**
- `200` - Session created successfully
- `401` - Not authenticated or invalid token
- `400` - User not found
- `500` - Server error

#### Get Session
**GET** `/api/v1/sessions/{session_id}`

Get complete session details by session_id.

**Path Parameters:**
- `session_id` (required) - Session ID

**Response:**
```json
{
  "session_id": "string",
  "user_id": "string",
  "job_details": {
    "job_role": "Senior Backend Engineer",
    "company_name": "Tech Corp",
    "company_url": "https://techcorp.com/jobs/123",
    "job_description": "We are looking for...",
    "parsed_requirements": [
      {
        "name": "Python",
        "type": "skill",
        "description": "5+ years experience",
        "priority": 5,
        "confidence": 0.95,
        "source": "ai_inferred",
        "value": null
      }
    ],
    "extracted_keywords": ["Python", "FastAPI", "MongoDB"]
  },
  "resume_state": {
    "stage": "job_analyzed",
    "required_fields": [...],
    "missing_fields": [],
    "ai_context": {
      "summary": "Analyzed job for Senior Backend Engineer at Tech Corp",
      "total_requirements": 15
    },
    "last_action": "job_analyzed"
  },
  "questionnaire": {
    "questions": [],
    "completion": 0.0
  },
  "last_active": "2025-11-02T12:00:00",
  "created_at": "2025-11-02T10:00:00"
}
```

**Status Codes:**
- `200` - Session retrieved successfully
- `404` - Session not found
- `500` - Server error

#### Get User Sessions
**GET** `/api/v1/sessions/user/{user_id}`

Get all sessions for a specific user, sorted by most recent activity.

**Path Parameters:**
- `user_id` (required) - User ID

**Response:**
```json
{
  "user_id": "string",
  "sessions": [
    {
      "session_id": "string",
      "user_id": "string",
      "job_details": {
        "job_role": "Senior Backend Engineer",
        "company_name": "Tech Corp",
        "company_url": "https://techcorp.com/jobs/123",
        "job_description": "We are looking for...",
        "parsed_requirements": [...],
        "extracted_keywords": [...]
      },
      "resume_state": {
        "stage": "job_analyzed",
        "required_fields": [...],
        "missing_fields": [],
        "ai_context": {...},
        "last_action": "job_analyzed"
      },
      "questionnaire": {
        "questions": [],
        "completion": 0.0
      },
      "last_active": "2025-11-02T12:00:00",
      "created_at": "2025-11-02T10:00:00"
    }
  ],
  "total_sessions": 1
}
```

**Status Codes:**
- `200` - Sessions retrieved successfully
- `404` - User not found
- `500` - Server error

#### Update Session
**PUT** `/api/v1/sessions`

Update session fields by session_id.

**Query Parameters:**
- `session_id` (required) - Session ID

**Request Body:**
```json
{
  "job_details": {
    "job_role": "string",
    "company_name": "string",
    "company_url": "string",
    "job_description": "string",
    "parsed_requirements": [
      {
        "name": "Python",
        "type": "skill",
        "description": "Backend development",
        "priority": 1,
        "confidence": 0.95,
        "source": "ai_inferred",
        "value": null
      }
    ],
    "extracted_keywords": ["Python", "FastAPI", "MongoDB"]
  },
  "resume_state": {
    "stage": "requirements_identified",
    "required_fields": [
      {
        "name": "Python experience",
        "type": "work_experience",
        "priority": 1,
        "confidence": 0.9
      }
    ],
    "missing_fields": [],
    "ai_context": {
      "summary": "Job requires backend skills"
    },
    "last_action": "requirements_analyzed"
  },
  "questionnaire": {
    "questions": [
      {
        "id": "q1",
        "question": "What Python frameworks have you used?",
        "related_field": "work_experience",
        "answer": null,
        "confidence": null,
        "status": "unanswered"
      }
    ],
    "completion": 0.0
  }
}
```

*Note: `session_id` cannot be updated. `last_active` is automatically updated. All fields are optional.*

**Resume Stage Values:**
- `init` - Session just created
- `job_analyzed` - Job description analyzed
- `requirements_identified` - Requirements extracted
- `questionnaire_pending` - Waiting for user responses
- `ready_for_resume` - All info collected
- `completed` - Resume generated
- `error` - Error occurred

**Response:**
```json
{
  "message": "Session updated successfully",
  "session_id": "string",
  "modified_count": 1
}
```

**Status Codes:**
- `200` - Session updated successfully
- `404` - Session not found
- `500` - Server error

---

### Job Questions

#### Generate Job Questions
**POST** `/api/v1/job-questions`

Generate tailored questions based on job details.

**Request Body:**
```json
{
  "job_role": "string",
  "company_name": "string",
  "company_url": "string",
  "job_description": "string"
}
```

**Response:**
```json
{
  "questions": ["string"],
  "total_questions": 0,
  "job_role": "string",
  "company_url": "string"
}
```

**Status Codes:**
- `200` - Questions generated successfully
- `500` - Server error
