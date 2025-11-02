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

### Sessions

#### Create Session
**POST** `/api/v1/sessions`

Create a new session for a user with job details.

**Query Parameters:**
- `user_id` (required) - User's ID

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
  "message": "Session created successfully",
  "session_id": "string",
  "user_id": "string"
}
```

**Status Codes:**
- `200` - Session created successfully
- `400` - User not found
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
    "job_description": "string"
  },
  "resume_state": {
    "status": "string",
    "missing_fields": ["string"]
  },
  "questionnaire": {
    "questions": ["string"],
    "answers": {
      "question": "answer"
    }
  }
}
```

*Note: `session_id` cannot be updated. `last_active` is automatically updated.*

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
