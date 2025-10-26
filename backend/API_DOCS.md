# API Documentation

## Base URL
`http://localhost:8000`

## Endpoints

### Users

#### Create User
**POST** `/api/v1/users`

Create a new user with personal details.

**Request Body:**
```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "socials": {
    "linkedin": "string"
  },
  "address": "string"
}
```

*Note: `user_id` is automatically generated if not provided.*

**Response:**
```json
{
  "message": "User created successfully",
  "user_id": "string"
}
```

**Status Codes:**
- `200` - User created successfully
- `400` - User with email already exists
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
  "address": "string"
}
```

*Note: `email` and `user_id` cannot be updated.*

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
