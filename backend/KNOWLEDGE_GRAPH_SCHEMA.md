# Knowledge Graph Schema Reference

This document defines the canonical schema for all knowledge graph data structures used across the resume builder application. **All AI prompts and data processing must follow these schemas exactly.**

## Schema Version
**Version:** 1.0
**Last Updated:** 2025-11-04

---

## Knowledge Graph Structure

The knowledge graph is organized into 7 main categories:

```python
{
  "education": [...]        # Array of education objects
  "work_experience": [...]  # Array of work experience objects
  "projects": [...]         # Array of project objects
  "certifications": [...]   # Array of certification objects
  "research_work": [...]    # Array of research work objects
  "skills": [...]           # Array of skill name strings
  "misc": {...}             # Dictionary for miscellaneous items
}
```

---

## Detailed Schemas

### 1. Education
**Type:** Array of objects
**Purpose:** Academic qualifications and degrees

```json
{
  "institution": "string (required)",
  "degree": "string (required)",
  "field": "string (optional)",
  "start_date": "string (optional, YYYY-MM or YYYY)",
  "end_date": "string (optional, YYYY-MM or YYYY or 'present')",
  "gpa": "string (optional)"
}
```

**Example:**
```json
{
  "institution": "Stanford University",
  "degree": "Bachelor of Science",
  "field": "Computer Science",
  "start_date": "2018-09",
  "end_date": "2022-06",
  "gpa": "3.8"
}
```

**Field Guidelines:**
- `institution`: Full university or college name
- `degree`: Degree type (e.g., "Bachelor of Science", "Master of Arts", "PhD")
- `field`: Major or field of study
- `start_date`/`end_date`: Use YYYY-MM format when month is known, YYYY otherwise
- `gpa`: Can be on any scale (3.8/4.0, 85%, etc.)

---

### 2. Work Experience
**Type:** Array of objects
**Purpose:** Professional work history

```json
{
  "company": "string (required)",
  "position": "string (required)",
  "start_date": "string (optional, YYYY-MM or YYYY)",
  "end_date": "string (optional, YYYY-MM or YYYY or 'present')",
  "description": "string (optional, SHORT BULLETED format)"
}
```

**Example:**
```json
{
  "company": "Google",
  "position": "Software Engineer",
  "start_date": "2022-07",
  "end_date": "present",
  "description": "• Developed backend services for search infrastructure\n• Improved query performance by 40%\n• Led team of 3 engineers on microservices migration"
}
```

**Field Guidelines:**
- `company`: Official company name
- `position`: Job title or role
- `start_date`/`end_date`: Use YYYY-MM when month is known, YYYY otherwise. Use "present" for current positions
- `description`: **MUST BE SHORT AND BULLETED**. Use "•" or "-" for bullets. Each bullet 1-2 lines max. Focus on impact and quantifiable results

---

### 3. Projects
**Type:** Array of objects
**Purpose:** Personal or professional projects

```json
{
  "name": "string (required)",
  "description": "string (required, SHORT BULLETED format)",
  "technologies": ["array", "of", "strings"] (optional)",
  "url": "string (optional)",
  "start_date": "string (optional, YYYY-MM or YYYY)",
  "end_date": "string (optional, YYYY-MM or YYYY or 'present')"
}
```

**Example:**
```json
{
  "name": "AI Resume Builder",
  "description": "• Web application that generates tailored resumes using AI\n• Allows users to input job descriptions and creates customized resumes\n• Supports multiple resume templates and export formats",
  "technologies": ["Python", "FastAPI", "MongoDB", "React", "AI/ML"],
  "url": "https://github.com/user/resume-builder",
  "start_date": "2024-01",
  "end_date": "present"
}
```

**Field Guidelines:**
- `name`: Clear, concise project name
- `description`: **MUST BE SHORT AND BULLETED**. Describe what it does, key features, and impact
- `technologies`: Array of specific technology names (not categories)
- `url`: GitHub repo, live demo, or project website
- `start_date`/`end_date`: Project timeline. Use "present" for ongoing projects

---

### 4. Certifications
**Type:** Array of objects
**Purpose:** Professional certifications and licenses

```json
{
  "name": "string (required)",
  "issuer": "string (optional)",
  "date": "string (optional, YYYY-MM or YYYY)",
  "credential_id": "string (optional)",
  "url": "string (optional)"
}
```

**Example:**
```json
{
  "name": "AWS Certified Solutions Architect",
  "issuer": "Amazon Web Services",
  "date": "2023-05",
  "credential_id": "AWS-12345-ABCDE",
  "url": "https://aws.amazon.com/verification/12345"
}
```

**Field Guidelines:**
- `name`: Full certification name
- `issuer`: Certifying organization
- `date`: When certification was obtained
- `credential_id`: Unique identifier for verification
- `url`: Verification or badge URL

---

### 5. Research Work
**Type:** Array of objects
**Purpose:** Published papers, research projects, academic work

```json
{
  "title": "string (required)",
  "venue": "string (optional)",
  "date": "string (optional, YYYY-MM or YYYY)",
  "description": "string (optional, SHORT BULLETED format)",
  "url": "string (optional)"
}
```

**Example:**
```json
{
  "title": "Efficient Neural Architecture Search Using Reinforcement Learning",
  "venue": "NeurIPS 2023",
  "date": "2023-12",
  "description": "• Proposed novel approach to automate neural network design\n• Achieved 15% improvement in search efficiency\n• Published at top-tier ML conference",
  "url": "https://arxiv.org/abs/12345"
}
```

**Field Guidelines:**
- `title`: Full paper or research project title
- `venue`: Conference, journal, or publication venue
- `date`: Publication or completion date
- `description`: **MUST BE SHORT AND BULLETED** if provided. Key findings or contributions
- `url`: arXiv, DOI, or publication link

---

### 6. Skills
**Type:** Array of strings
**Purpose:** Technical and soft skills

```json
["Python", "JavaScript", "Docker", "Kubernetes", "Leadership", "Public Speaking"]
```

**Guidelines:**
- Store **ONLY** skill names, not descriptions or proficiency levels
- Use standard/canonical names (e.g., "JavaScript" not "JS", "Python" not "python")
- Single words or short phrases
- Include both technical skills and soft skills
- Avoid duplicates
- No nested objects or additional metadata

**Example:**
```json
[
  "Python",
  "FastAPI",
  "React",
  "MongoDB",
  "Docker",
  "Kubernetes",
  "AWS",
  "Machine Learning",
  "Leadership",
  "Agile Methodologies"
]
```

---

### 7. Misc
**Type:** Dictionary (key-value pairs)
**Purpose:** Truly miscellaneous information that doesn't fit other categories

```json
{
  "languages": ["English", "Spanish", "French"],
  "hobbies": ["Photography", "Hiking"],
  "volunteer_work": "Volunteer coding instructor at local community center"
}
```

**Guidelines:**
- Use for information that genuinely doesn't fit other categories
- Examples: languages spoken, hobbies, volunteer work, awards not tied to work/education
- Should be **minimal** - most professional data belongs in other categories
- Flexible structure, no strict schema
- **DO NOT** use for skills, experience, projects, certifications, education, or research

---

## Data Consistency Rules

### Date Formats
- **Preferred:** YYYY-MM (e.g., "2023-05")
- **Acceptable:** YYYY (e.g., "2023")
- **Current positions:** "present" (lowercase)
- **Never use:** "Present", "PRESENT", "ongoing", "current"

### Description Formatting
All description fields MUST follow these rules:
1. **SHORT AND BULLETED** - No long paragraphs
2. Use "•" or "-" for bullet points
3. Each bullet 1-2 lines maximum
4. Separate bullets with `\n` (newline character)
5. Focus on impact and quantifiable results
6. Start with action verbs (Developed, Improved, Led, Built, etc.)

**Good Example:**
```
"• Developed backend services for search infrastructure\n• Improved query performance by 40%\n• Led team of 3 engineers"
```

**Bad Example:**
```
"I worked on developing various backend services for the search infrastructure team where I was responsible for improving performance and leading a team and doing various other tasks..."
```

### Required vs Optional Fields
- **Required fields** must have a non-empty value
- **Optional fields** can be empty strings (`""`) or omitted entirely
- Empty arrays (`[]`) are acceptable for optional array fields
- Empty objects (`{}`) are acceptable for misc

### Technology Names
- Use official/canonical names
- Capitalize properly (e.g., "JavaScript" not "javascript")
- Use full names when ambiguous (e.g., "React.js" or "React")
- Group related items appropriately (e.g., "Python", "FastAPI" as separate items)

---

## Schema Validation

### Before Adding to Knowledge Graph
1. Verify category is one of: education, work_experience, projects, certifications, research_work, skills, misc
2. Check all required fields are present and non-empty
3. Validate date formats (YYYY-MM or YYYY or "present")
4. Ensure descriptions are SHORT and BULLETED
5. Verify skills are simple strings, not objects
6. Confirm misc is only used for truly miscellaneous items

### Common Mistakes to Avoid
❌ Storing experience data in misc
❌ Adding proficiency levels to skills array
❌ Using long paragraph descriptions
❌ Inconsistent date formats
❌ Nested or complex structures in skills
❌ Missing required fields
❌ Using "Present" instead of "present"

---

## AI Implementation Notes

**For AI agents processing user data:**

1. **Always** extract data into the most specific category possible
2. **Never** put professional data (work, projects, education, certs) in misc
3. **Always** format descriptions as SHORT, BULLETED points
4. **Always** extract technology names separately in the technologies array
5. **Always** use standardized date formats
6. **Always** include all schema fields, even if empty
7. **Always** return confidence scores for data quality assessment

**Example AI response structure:**
```json
{
  "category": "projects",
  "data": {
    "name": "AI Resume Builder",
    "description": "• Web application for resume generation\n• Uses AI for personalization",
    "technologies": ["Python", "FastAPI", "AI/ML"],
    "url": "",
    "start_date": "",
    "end_date": ""
  },
  "confidence": 0.8,
  "reasoning": "Clear project description with technologies mentioned"
}
```

---

## Schema Evolution

When updating this schema:
1. Update this document first
2. Update all AI agent prompts in `app/ai/agent.py`
3. Update API documentation in `API_DOCS.md`
4. Update examples in `CLAUDE.md`
5. Add migration logic if changing existing data structures
6. Test with existing knowledge graphs to ensure compatibility

---

## References

- **Implementation:** `app/ai/agent.py`
- **Database Models:** `app/database/models.py` - `KnowledgeGraph` class
- **API Endpoints:** `app/routers/ai.py` - `/parse-text`, `/optimize-knowledge-graph`, `/answer-question`
- **API Documentation:** `API_DOCS.md`
- **Developer Guide:** `CLAUDE.md`
