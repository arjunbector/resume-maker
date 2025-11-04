# API Documentation

## Base URL
`http://localhost:8000`

## Authentication

All protected endpoints support two authentication methods:
1. **Cookie-based:** `access_token` cookie (set automatically on login/signup)
2. **Header-based:** `Authorization: Bearer {token}` header

The server checks for the token in cookies first, then falls back to the Authorization header.

**Cookie Configuration:**
- `httpOnly: true` - Prevents XSS attacks
- `samesite: "none"` - Allows cross-origin requests
- `secure: true` - Requires HTTPS
- `max_age: 30 days` - Token expiration

**Frontend Requirements:**
When making requests from a frontend on a different origin, you MUST include credentials:
- **fetch:** `credentials: 'include'`
- **axios:** `withCredentials: true`

Example:
```javascript
// fetch
fetch('http://127.0.0.1:8000/api/v1/users', {
  credentials: 'include'
})

// axios
axios.get('http://127.0.0.1:8000/api/v1/users', {
  withCredentials: true
})
```

## Complete Workflow

### Resume Building Flow

1. **User Authentication**
   - Sign up: `POST /api/v1/auth/signup`
   - Login: `POST /api/v1/auth/login`
   - Get profile: `GET /api/v1/auth/me`

2. **Build User Profile**
   - Update basic info: `PUT /api/v1/users` (name, phone, current_job_title)
   - Add knowledge graph data: `POST /api/v1/users/knowledge-graph/add`

3. **Create Resume Session**
   - Create blank session: `POST /api/v1/sessions/new`
   - Returns `session_id` for tracking

4. **Analyze Job Posting**
   - Analyze job: `POST /api/v1/ai/analyze`
   - Provide job description, role, company name
   - AI extracts requirements and keywords
   - Session updated with parsed requirements
   - Stage: `JOB_ANALYZED`

5. **Compare with Profile**
   - Compare: `POST /api/v1/ai/compare?session_id=...`
   - AI identifies missing and matched fields
   - **If no missing fields:** Stage → `READY_FOR_RESUME`
   - **If missing fields:** Stage → `REQUIREMENTS_IDENTIFIED`

6. **Fill Missing Information** (if needed)
   - Generate questionnaire: `POST /api/v1/ai/generate-questionnaire?session_id=...`
   - AI creates short, targeted questions
   - Stage: `QUESTIONNAIRE_PENDING`
   - Answer questions: `POST /api/v1/ai/answer-question` (repeat for each)
   - Each answer automatically updates knowledge graph
   - When all answered: Stage → `READY_FOR_RESUME`

7. **Generate Resume** (to be implemented)
   - Use session data to generate tailored resume
   - Stage: `COMPLETED`

**Session States:**
- `INIT` - Session created
- `JOB_ANALYZED` - Job requirements extracted
- `REQUIREMENTS_IDENTIFIED` - Missing fields identified
- `QUESTIONNAIRE_PENDING` - Questions generated, awaiting answers
- `READY_FOR_RESUME` - All data collected, ready for generation
- `COMPLETED` - Resume generated
- `ERROR` - Error occurred

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
  "resume_email": "string",
  "current_job_title": "string",
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

Get current authenticated user's profile. Uses authentication (cookie or Authorization header) to automatically identify the user.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Response:**
```json
{
  "user_id": "string",
  "name": "string",
  "email": "string",
  "phone": "string",
  "current_job_title": "string",
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
- `401` - Not authenticated or invalid token
- `404` - User not found
- `500` - Server error

#### Update User
**PUT** `/api/v1/users`

Update current authenticated user's profile. Uses authentication (cookie or Authorization header) to automatically identify the user.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "name": "string",
  "phone": "string",
  "resume_email": "string",
  "current_job_title": "string",
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

*Note: `email`, `user_id`, and `hashed_password` cannot be updated. All fields are optional. User is identified automatically via authentication.*

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
- `401` - Not authenticated or invalid token
- `404` - User not found
- `500` - Server error

---

#### Set Knowledge Graph Data
**POST** `/api/v1/users/knowledge-graph/add`

Set/replace items in different categories of the user's knowledge graph. This endpoint directly sets the provided data, replacing existing data in those categories.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "education": [
    {
      "institution": "Stanford University",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "start_date": "2018-09",
      "end_date": "2022-06",
      "gpa": "3.8"
    }
  ],
  "work_experience": [
    {
      "company": "Google",
      "position": "Software Engineer",
      "start_date": "2022-07",
      "end_date": "present",
      "description": "Worked on search infrastructure"
    }
  ],
  "projects": [
    {
      "name": "Resume Builder",
      "description": "AI-powered resume builder using FastAPI and MongoDB",
      "technologies": ["Python", "FastAPI", "MongoDB", "React"],
      "url": "https://github.com/user/resume-builder"
    }
  ],
  "certifications": [
    {
      "name": "AWS Certified Solutions Architect",
      "issuer": "Amazon Web Services",
      "date": "2023-05",
      "credential_id": "ABC123"
    }
  ],
  "skills": ["Python", "FastAPI", "Docker", "Kubernetes"],
  "research_work": [],
  "misc": {
    "languages": ["English", "Spanish"],
    "hobbies": ["Photography", "Hiking"]
  }
}
```

**Recommended Schemas for Knowledge Graph Items:**

**Education:**
```json
{
  "institution": "Stanford University",
  "degree": "Bachelor of Science",
  "field": "Computer Science",
  "start_date": "2018-09",
  "end_date": "2022-06"
}
```

**Work Experience:**
```json
{
  "company": "Google",
  "position": "Software Engineer",
  "start_date": "2022-07",
  "end_date": "present",
  "description": "Brief description of responsibilities"
}
```

**Projects:**
```json
{
  "name": "Resume Builder",
  "description": "AI-powered resume builder",
  "technologies": ["Python", "FastAPI", "MongoDB"]
}
```

**Certifications:**
```json
{
  "name": "AWS Certified Solutions Architect",
  "issuer": "Amazon Web Services",
  "date": "2023-05"
}
```

**Research Work:**
```json
{
  "title": "Machine Learning for NLP",
  "venue": "IEEE Conference",
  "date": "2023-08"
}
```

**Skills:**
```json
["Python", "JavaScript", "Docker", "Machine Learning"]
```

**Misc:**
```json
{
  "languages": ["English", "Spanish"],
  "awards": ["Best Employee 2023"]
}
```

**Notes:**
- All fields are optional - you can update one or multiple categories
- Items are **SET directly**, replacing existing data in those categories
- Only the categories provided in the request will be updated
- Categories not included in the request will remain unchanged
- To add items to existing data, fetch current data first, merge it, then set the complete array
- The schemas above are recommended but flexible - you can include additional fields as needed

**Example - Setting only skills:**
```json
{
  "skills": ["React", "Node.js", "TypeScript"]
}
```

**Example - Setting multiple categories:**
```json
{
  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "Full-stack e-commerce application",
      "technologies": ["React", "Node.js", "PostgreSQL"]
    }
  ],
  "skills": ["PostgreSQL", "Redis"],
  "certifications": [
    {
      "name": "Docker Certified Associate",
      "issuer": "Docker",
      "date": "2024-01"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Knowledge graph items set successfully",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "set_items": {
    "education": 1,
    "work_experience": 1,
    "projects": 1,
    "certifications": 1,
    "skills": 3
  },
  "total_items_set": 7
}
```

**Response Fields:**
- `set_items`: Breakdown of how many items were set in each category
- `total_items_set`: Total number of items set across all categories

**Status Codes:**
- `200` - Items set successfully
- `400` - No items provided to set
- `401` - Not authenticated or invalid token
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

#### Generate Questionnaire
**POST** `/api/v1/ai/generate-questionnaire`

Generate a contextual questionnaire based on missing fields identified in the session. The AI creates specific questions for each missing requirement to help the user fill in profile gaps.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Query Parameters:**
- `session_id` (required) - Session ID with identified missing fields

**Example Request:**
```
POST /api/v1/ai/generate-questionnaire?session_id=550e8400-e29b-41d4-a716-446655440000
```

**Prerequisites:**
- Session must exist and belong to the authenticated user
- Session must have missing fields identified using `/api/v1/ai/compare`
- Resume state must have `missing_fields` populated

**Response:**
```json
{
  "message": "Questionnaire generated successfully",
  "user_id": "user-uuid-here",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_questions": 3,
  "completion": 0.0,
  "questions": [
    {
      "id": "q-uuid-1",
      "question": "Do you have experience with Docker? If yes, please describe your proficiency level and any projects where you've used Docker for containerization.",
      "related_field": "Docker",
      "answer": null,
      "confidence": null,
      "status": "unanswered"
    },
    {
      "id": "q-uuid-2",
      "question": "Have you worked with Kubernetes for container orchestration? Please describe your experience level and any relevant projects or certifications.",
      "related_field": "Kubernetes",
      "answer": null,
      "confidence": null,
      "status": "unanswered"
    },
    {
      "id": "q-uuid-3",
      "question": "Do you have experience designing and implementing microservices architecture? Please provide details about the scale and technologies used.",
      "related_field": "Microservices",
      "answer": null,
      "confidence": null,
      "status": "unanswered"
    }
  ]
}
```

**What This Endpoint Does:**
1. Retrieves the session and verifies ownership
2. Extracts missing fields from the session's resume state
3. Uses AI to generate contextual, specific questions for each missing field
4. Creates unique question IDs for tracking
5. Updates the session's questionnaire with generated questions
6. Sets stage to `QUESTIONNAIRE_PENDING`
7. Initializes completion to 0.0 (no questions answered yet)

**Question Types by Field:**
- **Skills**: Questions about proficiency level and project examples
- **Education**: Questions about institution, degree, field of study, dates
- **Certifications**: Questions about certification name, issuer, date obtained
- **Experience**: Questions about company, role, duration, responsibilities
- **Projects**: Questions about project name, description, technologies used

**Session Updates:**
The endpoint automatically updates the session with:
- `questionnaire.questions`: List of generated QuestionItem objects
- `questionnaire.completion`: Set to 0.0 (no answers yet)
- `resume_state.stage`: Set to `QUESTIONNAIRE_PENDING`
- `resume_state.ai_context`: Summary with total questions and progress
- `resume_state.last_action`: Set to `questionnaire_generated`

**Question Item Schema:**
- `id`: Unique identifier for the question (UUID)
- `question`: The actual question text generated by AI
- `related_field`: Name of the missing field this question addresses
- `answer`: User's answer (null until answered)
- `confidence`: AI confidence in the answer quality (null until answered)
- `status`: Question status ("unanswered", "answered", or "reviewed")

**Status Codes:**
- `200` - Questionnaire generated successfully
- `400` - Session has no missing fields (need to compare first)
- `401` - Not authenticated or invalid token
- `403` - Session does not belong to authenticated user
- `404` - Session not found
- `500` - Server error

---

#### Answer Question
**POST** `/api/v1/ai/answer-question`

Submit an answer to a questionnaire question. The AI processes the answer, extracts structured information, and automatically updates both the session questionnaire and the user's knowledge graph.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question_id": "q-uuid-1",
  "answer": "I have intermediate level experience with Docker, used it in 3 production projects"
}
```

**Prerequisites:**
- Session must exist and belong to authenticated user
- Question must exist in the session's questionnaire
- Questionnaire must have been generated using `/api/v1/ai/generate-questionnaire`

**Response:**
```json
{
  "message": "Answer submitted successfully",
  "user_id": "user-uuid-here",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question_id": "q-uuid-1",
  "confidence": 0.8,
  "completion": 33.33,
  "answered_count": 1,
  "total_questions": 3,
  "knowledge_graph_updated": true,
  "extracted_data": "Added Docker skill with intermediate proficiency",
  "all_questions_answered": false
}
```

**What This Endpoint Does:**
1. Retrieves the session and validates ownership
2. Finds the specific question by question_id
3. Uses AI to process the answer and extract structured data
4. Determines which knowledge graph category to update (education, skills, projects, etc.)
5. Updates the question with the answer, confidence score, and status
6. Calculates questionnaire completion percentage
7. Updates the user's knowledge graph with extracted information
8. Advances stage to `READY_FOR_RESUME` when all questions are answered

**Knowledge Graph Auto-Update:**
The AI automatically extracts relevant information from answers and adds it to the appropriate knowledge graph category:
- **Skills**: Extracts skill names from answers about technical abilities
- **Education**: Structures degree, institution, dates from education answers
- **Work Experience**: Extracts company, position, dates, description from experience answers
- **Projects**: Structures project name, description, technologies from project answers
- **Certifications**: Extracts certification name, issuer, date from certification answers
- **Research Work**: Structures title, venue, date from research answers

**Answer Confidence Scoring:**
The AI assigns a confidence score (0.0-1.0) based on answer quality:
- **0.7-1.0**: Detailed, complete answer with specific information
- **0.5-0.7**: Adequate answer with some details
- **0.3-0.5**: Vague or incomplete answer
- **0.0-0.3**: Unclear answer or "no/none" responses

**Session Updates:**
The endpoint automatically updates:
- `questionnaire.questions[index]`: Updates the specific question with answer, confidence, and status
- `questionnaire.completion`: Percentage of answered questions (0-100)
- `resume_state.stage`: Set to `READY_FOR_RESUME` when completion reaches 100%
- `resume_state.ai_context`: Summary with answer progress and extraction details
- `resume_state.last_action`: Set to `question_answered`

**Response Fields:**
- `confidence`: AI confidence in the answer quality (0.0-1.0)
- `completion`: Percentage of questions answered
- `knowledge_graph_updated`: Whether the knowledge graph was updated with extracted data
- `extracted_data`: Summary of what information was extracted from the answer
- `all_questions_answered`: Boolean indicating if questionnaire is complete

**Notes:**
- Answers can be updated by submitting again with the same question_id
- Knowledge graph updates are additive (new items are appended)
- If AI fails to extract structured data, the answer is still saved
- Empty or "no/none" answers are saved with low confidence

**Status Codes:**
- `200` - Answer submitted successfully
- `401` - Not authenticated or invalid token
- `403` - Session does not belong to authenticated user
- `404` - Session or question not found
- `500` - Server error

---

#### Optimize Knowledge Graph
**POST** `/api/v1/ai/optimize-knowledge-graph`

Analyze and automatically restructure the user's knowledge graph using AI. Identifies misplaced items and moves them to appropriate sections for better resume organization.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Request Body:**
None (uses authenticated user's knowledge graph)

**What This Endpoint Does:**
Uses AI to identify and fix common knowledge graph organization issues:
1. **Misc to Work Experience**: Moves items like `"FastAPI_experience": "5 years"` to work_experience
2. **Misc to Skills**: Extracts skill names from verbose descriptions
3. **Misc to Certifications**: Moves certifications to proper section
4. **Misc to Projects**: Moves project descriptions to projects section
5. **Skill Extraction**: Converts detailed descriptions into proper skill entries

**Example Input (Before Optimization):**
```json
{
  "education": [],
  "work_experience": [],
  "projects": [],
  "skills": ["Python", "Rust", "C"],
  "certifications": [],
  "research_work": [],
  "misc": {
    "FastAPI_experience": "5 years",
    "AWS_cert": "Solutions Architect 2023",
    "languages": ["English", "Spanish"]
  }
}
```

**Example Output (After Optimization):**
```json
{
  "message": "Knowledge graph optimized successfully",
  "user_id": "user-uuid-here",
  "email": "user@example.com",
  "changes_made": [
    "Moved 'FastAPI_experience: 5 years' from misc to work_experience",
    "Moved 'AWS_cert' from misc to certifications",
    "Added 'FastAPI' to skills"
  ],
  "total_changes": 3,
  "suggestions": [
    "Consider adding company name and dates for FastAPI work experience",
    "Add credential ID for AWS certification if available"
  ],
  "optimized_graph": {
    "education": [],
    "work_experience": [
      {
        "position": "Backend Developer (FastAPI)",
        "company": "",
        "start_date": "",
        "end_date": "",
        "description": "5 years of experience with FastAPI"
      }
    ],
    "projects": [],
    "skills": ["Python", "Rust", "C", "FastAPI"],
    "certifications": [
      {
        "name": "AWS Solutions Architect",
        "issuer": "Amazon Web Services",
        "date": "2023"
      }
    ],
    "research_work": [],
    "misc": {
      "languages": ["English", "Spanish"]
    }
  }
}
```

**Response Fields:**
- `message`: Success message or indication that no changes were needed
- `changes_made`: Array of human-readable descriptions of changes
- `total_changes`: Number of changes made
- `suggestions`: AI suggestions for further improving the knowledge graph
- `optimized_graph`: The complete restructured knowledge graph

**Automatic Update:**
The user's knowledge graph is automatically updated with the optimized structure if changes are made.

**When to Use:**
- After bulk importing data that may be unstructured
- When misc section has grown too large
- Before generating a resume to ensure proper categorization
- Periodically to maintain clean data structure

**Status Codes:**
- `200` - Knowledge graph optimized successfully
- `400` - Knowledge graph is empty (add data first)
- `401` - Not authenticated or invalid token
- `404` - User not found
- `500` - Server error or AI optimization failed

---

#### Parse Free-Form Text to Knowledge Graph
**POST** `/api/v1/ai/parse-text`

Parse free-form text into structured knowledge graph data. The AI automatically detects the type of information (project, education, work experience, certification, research work, skills) and structures it according to the appropriate schema. The parsed data is then added to the authenticated user's knowledge graph.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "text": "string (required)"
}
```

**Example Requests:**

**Example 1: Project Description**
```json
{
  "text": "I have built a website that lets you build resumes using AI using python and fastapi"
}
```

**Example 2: Work Experience**
```json
{
  "text": "I worked at Google as a Software Engineer from 2020 to 2023, where I developed backend services for search infrastructure and worked with Python and Go"
}
```

**Example 3: Education**
```json
{
  "text": "Bachelor of Science in Computer Science from Stanford University, graduated 2022 with 3.8 GPA"
}
```

**Example 4: Skills**
```json
{
  "text": "I know Python, JavaScript, Docker, Kubernetes, and AWS"
}
```

**Response:**
```json
{
  "message": "Successfully parsed text and added to {category}",
  "user_id": "string",
  "email": "string",
  "category": "projects",
  "data": {
    "name": "AI Resume Builder",
    "description": "• Web application that generates tailored resumes using AI\n• Allows users to input job descriptions and automatically creates customized resumes\n• Built with Python backend and AI integration",
    "technologies": ["Python", "FastAPI", "AI/ML"],
    "url": "",
    "start_date": "",
    "end_date": ""
  },
  "confidence": 0.8,
  "reasoning": "Clearly describes a project with technical details. Extracted programming languages and framework.",
  "knowledge_graph_updated": true
}
```

**Knowledge Graph Schemas:**

The endpoint uses the following schemas for different categories:

1. **Education:**
   - `institution` (string, required): University or college name
   - `degree` (string, required): Degree type (e.g., "Bachelor of Science")
   - `field` (string, optional): Field of study
   - `start_date` (string, optional): YYYY-MM or YYYY format
   - `end_date` (string, optional): YYYY-MM or YYYY or "present"
   - `gpa` (string, optional): GPA or grade

2. **Work Experience:**
   - `company` (string, required): Company name
   - `position` (string, required): Job title
   - `start_date` (string, optional): YYYY-MM or YYYY format
   - `end_date` (string, optional): YYYY-MM or YYYY or "present"
   - `description` (string, optional): SHORT, BULLETED responsibilities and achievements

3. **Projects:**
   - `name` (string, required): Project name
   - `description` (string, required): SHORT, BULLETED project description
   - `technologies` (array, optional): List of technologies used
   - `url` (string, optional): Project URL or repository
   - `start_date` (string, optional): YYYY-MM or YYYY format
   - `end_date` (string, optional): YYYY-MM or YYYY or "present"

4. **Certifications:**
   - `name` (string, required): Certification name
   - `issuer` (string, optional): Issuing organization
   - `date` (string, optional): YYYY-MM or YYYY format
   - `credential_id` (string, optional): Credential ID
   - `url` (string, optional): Verification URL

5. **Research Work:**
   - `title` (string, required): Paper or research title
   - `venue` (string, optional): Conference or journal name
   - `date` (string, optional): YYYY-MM or YYYY format
   - `description` (string, optional): SHORT, BULLETED summary
   - `url` (string, optional): Publication URL

6. **Skills:**
   - Array of skill names (e.g., `["Python", "FastAPI", "Docker"]`)

**Important Notes:**
- Descriptions are automatically formatted as SHORT, BULLETED points
- Each bullet point is 1-2 lines maximum
- Technologies and tools mentioned in text are extracted automatically
- Dates are formatted as YYYY-MM or YYYY
- The AI determines the best category based on content
- Confidence score (0.0-1.0) indicates parsing quality
- For skills, duplicates are automatically avoided
- Data is immediately added to user's knowledge graph

**Response Fields:**
- `message`: Success message
- `user_id`: User's ID
- `email`: User's email
- `category`: Detected category (projects, education, work_experience, etc.)
- `data`: Structured data according to category schema
- `confidence`: AI confidence score (0.0-1.0)
- `reasoning`: Explanation of categorization and extraction
- `knowledge_graph_updated`: Whether data was added to knowledge graph

**Use Cases:**
1. **Quick Data Entry**: Users can describe their experience in natural language
2. **Bulk Import**: Parse resumes or profiles from other formats
3. **Voice Input**: Convert voice-to-text descriptions into structured data
4. **Mobile-Friendly**: Easier than filling complex forms
5. **Smart Extraction**: AI extracts technologies, dates, and other metadata automatically

**Status Codes:**
- `200` - Text parsed and added to knowledge graph successfully
- `400` - Text input is empty or invalid
- `401` - Not authenticated or invalid token
- `404` - User not found
- `500` - Server error or AI parsing failed

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
  "resume_name": "My Software Engineer Resume",
  "resume_description": "Tailored for Tech Corp Senior Backend position",
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
**GET** `/api/v1/sessions/user/all`

Get all sessions for the authenticated user, sorted by most recent activity. Uses authentication (cookie or Authorization header) to automatically identify the user.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Response:**
```json
{
  "user_id": "string",
  "sessions": [
    {
      "session_id": "string",
      "user_id": "string",
      "resume_name": "My Software Engineer Resume",
      "resume_description": "Tailored for Tech Corp Senior Backend position",
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
- `401` - Not authenticated or invalid token
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

#### Get Resume Data
**GET** `/api/v1/sessions/{session_id}/resume-data`

Get complete, structured resume data for a session. Combines user profile and session data into a single response ready for resume generation.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Path Parameters:**
- `session_id` (required) - Session ID

**Response:**
```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john.doe@gmail.com",
    "phone": "+1234567890",
    "address": "San Francisco, CA",
    "current_job_title": "Senior Software Engineer",
    "socials": {
      "linkedin": "https://linkedin.com/in/johndoe",
      "github": "https://github.com/johndoe"
    }
  },
  "professional_profile": {
    "education": [
      {
        "institution": "Stanford University",
        "degree": "Bachelor of Science",
        "field": "Computer Science",
        "start_date": "2018-09",
        "end_date": "2022-06"
      }
    ],
    "work_experience": [
      {
        "company": "Google",
        "position": "Software Engineer",
        "start_date": "2022-07",
        "end_date": "present",
        "description": "Backend development with Python and Go"
      }
    ],
    "projects": [
      {
        "name": "Resume Builder",
        "description": "AI-powered resume builder",
        "technologies": ["Python", "FastAPI", "MongoDB", "React"]
      }
    ],
    "skills": ["Python", "FastAPI", "MongoDB", "React", "Docker"],
    "certifications": [
      {
        "name": "AWS Certified Solutions Architect",
        "issuer": "Amazon Web Services",
        "date": "2023-05"
      }
    ],
    "research_work": [],
    "misc": {}
  },
  "target_job": {
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
        "confidence": 0.95
      }
    ],
    "extracted_keywords": ["Python", "FastAPI", "MongoDB"]
  },
  "resume_metadata": {
    "resume_name": "Tech Corp Backend Engineer Resume",
    "resume_description": "Tailored for Senior Backend Engineer at Tech Corp",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-11-02T10:00:00",
    "last_active": "2025-11-02T12:00:00"
  },
  "analysis": {
    "stage": "ready_for_resume",
    "missing_fields": [],
    "required_fields": [
      {
        "name": "Python",
        "type": "skill",
        "priority": 5,
        "confidence": 0.95
      }
    ],
    "ai_context": {
      "summary": "Compared job requirements with user profile",
      "total_missing": 0,
      "total_matched": 10
    },
    "last_action": "requirements_compared"
  },
  "questionnaire": {
    "questions": [],
    "completion": 100.0
  }
}
```

**What This Endpoint Returns:**

1. **personal_info**: Contact information and current job title
   - Uses `resume_email` if set, otherwise falls back to account email
   - Includes all social links (LinkedIn, GitHub, etc.)

2. **professional_profile**: Complete knowledge graph
   - Education history
   - Work experience
   - Projects
   - Skills
   - Certifications
   - Research work
   - Miscellaneous information

3. **target_job**: Job-specific information
   - Role and company details
   - AI-parsed requirements
   - Extracted keywords from job description

4. **resume_metadata**: Session information
   - Resume name and description
   - Session ID and timestamps

5. **analysis**: AI analysis results
   - Current workflow stage
   - Missing and required fields
   - AI context and suggestions

6. **questionnaire**: Questions and answers
   - All questions with answers
   - Completion percentage

**Use Cases:**
- Generate resume PDF/document
- Display resume preview
- Check if all required data is available
- Frontend form population

**Status Codes:**
- `200` - Resume data retrieved successfully
- `401` - Not authenticated or invalid token
- `403` - Session does not belong to authenticated user
- `404` - Session not found
- `500` - Server error

---

#### Get All Resume Data
**GET** `/api/v1/sessions/user/all/resume-data`

Get complete, structured resume data for ALL sessions of the authenticated user. Returns an array of resume data objects, one for each session, with the same structure as the single session endpoint.

**Authentication Required:**
- Cookie: `access_token` OR
- Header: `Authorization: Bearer {token}`

**Request Parameters:**
None (uses authentication to identify user)

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_sessions": 3,
  "resume_data": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "personal_info": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0123",
        "address": "123 Main St, San Francisco, CA",
        "current_job_title": "Senior Software Engineer",
        "socials": {
          "linkedin": "https://linkedin.com/in/johndoe",
          "github": "https://github.com/johndoe"
        }
      },
      "professional_profile": {
        "education": [...],
        "work_experience": [...],
        "projects": [...],
        "skills": [...],
        "certifications": [...],
        "research_work": [...],
        "misc": {}
      },
      "target_job": {
        "job_role": "Senior Backend Engineer",
        "company_name": "Tech Corp",
        "company_url": "https://techcorp.com/jobs/123",
        "job_description": "...",
        "parsed_requirements": [...],
        "extracted_keywords": [...]
      },
      "resume_metadata": {
        "resume_name": "Tech Corp Backend Engineer Resume",
        "resume_description": "Tailored for Senior Backend Engineer at Tech Corp",
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2025-11-02T10:00:00",
        "last_active": "2025-11-02T12:00:00"
      },
      "analysis": {
        "stage": "ready_for_resume",
        "missing_fields": [],
        "required_fields": [...],
        "ai_context": {...},
        "last_action": "requirements_compared"
      },
      "questionnaire": {
        "questions": [],
        "completion": 100.0
      }
    },
    {
      "session_id": "660e8400-e29b-41d4-a716-446655440001",
      "personal_info": { /* Same as above */ },
      "professional_profile": { /* Same as above */ },
      "target_job": {
        "job_role": "Lead Engineer",
        "company_name": "Startup Inc",
        "company_url": "https://startup.com/careers",
        "job_description": "...",
        "parsed_requirements": [...],
        "extracted_keywords": [...]
      },
      "resume_metadata": {
        "resume_name": "Startup Lead Engineer Resume",
        "resume_description": "Tailored for Lead Engineer at Startup Inc",
        "session_id": "660e8400-e29b-41d4-a716-446655440001",
        "created_at": "2025-11-01T08:00:00",
        "last_active": "2025-11-01T15:00:00"
      },
      "analysis": { /* Session-specific */ },
      "questionnaire": { /* Session-specific */ }
    }
    // ... more sessions
  ]
}
```

**Response Structure:**
- `user_id`: The authenticated user's ID
- `total_sessions`: Total number of sessions found
- `resume_data`: Array of resume data objects (one per session)

**Each resume data object contains:**

0. **session_id**: Session identifier at top level for easy access (unique per session)

1. **personal_info**: Contact information (same across all sessions)
   - Name, email, phone, address, current job title
   - Social links (LinkedIn, GitHub, etc.)

2. **professional_profile**: Knowledge graph (same across all sessions)
   - Education, work experience, projects, skills
   - Certifications, research work, misc information

3. **target_job**: Job-specific information (unique per session)
   - Role, company, job description
   - AI-parsed requirements and keywords

4. **resume_metadata**: Session information (unique per session)
   - Resume name and description
   - Session ID (also included here for consistency)
   - Timestamps (created_at, last_active)

5. **analysis**: AI analysis results (unique per session)
   - Current workflow stage
   - Missing and required fields
   - AI context and suggestions

6. **questionnaire**: Questions and answers (unique per session)
   - All questions with user answers
   - Completion percentage

**Notes:**
- Each resume data object has `session_id` at the top level for easy access
- Session ID is also included in `resume_metadata` for consistency with single session endpoint
- Sessions are sorted by `last_active` (most recent first)
- Personal info and professional profile are the same across all sessions
- Target job, metadata, analysis, and questionnaire are unique per session
- If user has no sessions, returns empty array with `total_sessions: 0`
- This is efficient as it fetches user data once and reuses it for all sessions

**Use Cases:**
- Display all resumes/sessions in a dashboard
- Compare different resume versions
- Batch generate multiple resumes
- Export all resume data at once
- Show resume progress across different job applications

**Status Codes:**
- `200` - Resume data retrieved successfully (even if no sessions exist)
- `401` - Not authenticated or invalid token
- `404` - User not found
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
