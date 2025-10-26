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
