# Resume Maker

An AI-powered resume builder that creates tailored resumes by analysing job descriptions and matching them against a structured profile of the user's professional history.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Repository Structure](#repository-structure)
4. [Backend](#backend)
   - [Technology Stack](#backend-technology-stack)
   - [Entry Point & Application Lifecycle](#entry-point--application-lifecycle)
   - [Authentication & Security](#authentication--security)
   - [Database Layer](#database-layer)
   - [Data Models](#data-models)
   - [Knowledge Graph](#knowledge-graph)
   - [AI Layer](#ai-layer)
   - [Session State Machine](#session-state-machine)
   - [API Routers](#api-routers)
   - [Utilities](#utilities)
5. [Frontend](#frontend)
   - [Technology Stack](#frontend-technology-stack)
   - [Application Routes](#application-routes)
   - [Resume Editor Workflow](#resume-editor-workflow)
   - [Component Architecture](#component-architecture)
   - [State & Data Management](#state--data-management)
   - [Form Validation](#form-validation)
6. [End-to-End Resume Building Flow](#end-to-end-resume-building-flow)
7. [Deployment](#deployment)
8. [Environment Variables](#environment-variables)

---

## Project Overview

Resume Maker is a full-stack web application split into two independent services:

- **Backend** – a Python REST API that handles authentication, persists user profile data in a Knowledge Graph, orchestrates an AI agent to analyse job postings, and manages the resume-building session lifecycle.
- **Frontend** – a Next.js application that provides a multi-step resume editor, a live preview pane, and an AI-assisted questionnaire that fills gaps in the user's profile.

The application's core idea is that rather than forcing the user to write a generic resume, it first builds a rich, structured knowledge graph of their professional history and then, for each new job application, uses an AI agent to identify and fill any gaps before generating a perfectly tailored resume.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User Browser                      │
│                                                     │
│  Next.js 15 Frontend (React 19, TypeScript)         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  Auth    │  │Resume Editor │  │ Live Preview  │ │
│  │  Pages   │  │ (multi-step) │  │  (print/PDF)  │ │
│  └──────────┘  └──────────────┘  └───────────────┘ │
└────────────────────────┬────────────────────────────┘
                         │ REST / JSON  (credentials: include)
                         │ NEXT_PUBLIC_API_URL
┌────────────────────────▼────────────────────────────┐
│              FastAPI Backend (Python 3.13)           │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐│
│  │  /auth   │  │ /users   │  │ /sessions  /ai     ││
│  │  Router  │  │  Router  │  │  Routers           ││
│  └──────────┘  └──────────┘  └────────┬───────────┘│
│                                        │             │
│              ┌─────────────────────────▼──────────┐ │
│              │          AI Layer                  │ │
│              │  ResumeAgent  JobQuestionsPipeline │ │
│              │  (smolagents + LiteLLM)            │ │
│              └─────────────────────────┬──────────┘ │
└────────────────────────────────────────┼────────────┘
                                         │
              ┌──────────────────────────┼────────────┐
              │                          │            │
              ▼                          ▼            ▼
         MongoDB                  Google Gemini   Ollama
         (users,                  2.5 Flash API  (local LLM,
          sessions)                              optional)
```

---

## Repository Structure

```
resume-maker/
├── backend/                   # FastAPI Python service
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── ai/                # AI agent and pipeline
│   │   ├── database/          # MongoDB client, models, operations
│   │   ├── routers/           # FastAPI route handlers
│   │   ├── services/          # Business-logic services
│   │   └── utils/             # Auth helpers, prompts, dependencies
│   ├── pyproject.toml         # Python dependencies (uv)
│   ├── Dockerfile             # Multi-stage Docker build
│   ├── API_DOCS.md            # Full REST API reference
│   └── KNOWLEDGE_GRAPH_SCHEMA.md  # Knowledge Graph field contracts
│
└── frontend/                  # Next.js TypeScript application
    ├── src/
    │   ├── app/               # Next.js App Router pages
    │   │   └── (main)/        # Authenticated route group
    │   │       ├── auth/      # Login & signup pages
    │   │       ├── editor/    # Multi-step resume editor
    │   │       └── resumes/   # Saved resumes list
    │   ├── components/        # Shared & UI components
    │   ├── hooks/             # Custom React hooks
    │   └── lib/               # API client, types, validations, utils
    ├── package.json
    └── next.config.ts
```

---

## Backend

### Backend Technology Stack

| Concern | Library / Tool |
|---|---|
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| Database driver | PyMongo |
| Data validation | Pydantic v2 |
| Authentication | python-jose (JWT HS256), bcrypt |
| AI orchestration | smolagents, LiteLLM |
| Primary LLM | Google Gemini 2.5 Flash |
| Secondary LLM | Ollama (local, optional) |
| Web scraping | BeautifulSoup4 |
| Logging | Loguru |
| Package manager | uv |
| Runtime | Python 3.13 |

---

### Entry Point & Application Lifecycle

`app/main.py` bootstraps the FastAPI application using an async lifespan context manager:

1. **Startup** – opens a MongoDB connection and instantiates the `ResumeAgent` singleton, which is stored on `app.state` so every request handler can access it without re-initialising the model.
2. **Runtime** – all four routers (`auth`, `users`, `sessions`, `ai`) are registered under the `/api/v1` prefix. CORS is configured to allow all origins (suitable for development; should be restricted in production).
3. **Shutdown** – the MongoDB connection is gracefully closed.

---

### Authentication & Security

Authentication is handled through two complementary mechanisms to support both browser and programmatic clients:

- **Cookie-based** – on successful login or signup the server sets an `httpOnly`, `secure`, `samesite=none` cookie named `access_token` with a 30-day TTL. The browser sends this cookie automatically on subsequent requests.
- **Bearer token** – clients that cannot use cookies (e.g., mobile apps, CLI tools) can pass `Authorization: Bearer {token}` in the request header.

The dependency `utils/dependencies.py::get_current_user` checks both locations in order (cookie first, then header) and resolves the current user for protected endpoints.

Tokens are JWT (HS256) signed with `SECRET_KEY`. Passwords are hashed with bcrypt before storage and verified with `bcrypt.checkpw` on login.

---

### Database Layer

`database/client.py` wraps a `pymongo.MongoClient` in a thin connection manager. The client exposes two MongoDB collections:

- **`users`** – stores user accounts and their embedded Knowledge Graphs.
- **`sessions`** – stores resume-building sessions, including job details, resume state, and questionnaire progress.

`database/operations.py` provides two static-method helper classes, `UserOperations` and `SessionOperations`, that encapsulate all direct MongoDB queries, keeping routers free from database implementation details.

---

### Data Models

All Pydantic models live in `database/models.py`:

| Model | Purpose |
|---|---|
| `User` | Full user document including embedded `KnowledgeGraph` |
| `UserResponse` | Public-safe projection of `User` (omits password hash) |
| `Session` | Resume-building session: links to a user, stores `JobDetails`, `ResumeState`, and `Questionnaire` |
| `JobDetails` | Job role, company, description, and AI-parsed requirements |
| `ResumeState` | Current pipeline stage and field lists (`required_fields`, `missing_fields`) |
| `Questionnaire` | List of `QuestionItem` objects with answered/unanswered status and completion percentage |
| `FieldMetadata` | A single requirement field with name, type, priority, confidence, and value |
| `KnowledgeGraph` | Structured user profile (see next section) |

---

### Knowledge Graph

The Knowledge Graph is the heart of the user's professional profile. It is stored as a sub-document inside the `User` collection and is the primary data source for resume generation.

It contains seven categories:

| Category | Type | Description |
|---|---|---|
| `education` | Array of objects | Academic qualifications: institution, degree, field, start/end dates, GPA |
| `work_experience` | Array of objects | Employment history: company, position, dates, bulleted description |
| `projects` | Array of objects | Personal/professional projects: name, description, technologies, URL, dates |
| `certifications` | Array of objects | Professional certifications: name, issuer, date, credential ID, URL |
| `research_work` | Array of objects | Published papers / academic work: title, venue, date, description, URL |
| `skills` | Array of strings | Canonical technology and soft skill names |
| `misc` | Dictionary | Language proficiency, hobbies, volunteer work, and other items that don't fit above |

The schema is formally documented in `KNOWLEDGE_GRAPH_SCHEMA.md`, which serves as the contract for all AI prompts. The agent always reads and writes to this schema so that the data remains consistent regardless of how it was collected (manual form entry, AI text parsing, or questionnaire answers).

---

### AI Layer

The AI layer is built on **smolagents** with **LiteLLM** as the model abstraction, enabling the same code to run against Google Gemini or a local Ollama instance.

#### `ResumeAgent` (`ai/agent.py`)

A wrapper around a `LiteLLMModel` that provides purpose-built methods used by the `/ai` router:

| Method | What it does |
|---|---|
| `analyze_job_requirements` | Parses a job description into a list of `FieldMetadata` requirements and a set of extracted keywords |
| `compare_with_profile` | Receives job requirements and the user's Knowledge Graph; returns which fields are present (`matched_fields`) and which are absent (`missing_fields`) |
| `generate_questionnaire` | Converts a list of missing fields into short, targeted plain-language questions |
| `answer_question` | Takes a single question and the user's free-text answer; returns structured data ready to be merged into the Knowledge Graph |
| `parse_text` | Extracts structured Knowledge Graph entries from arbitrary user-provided text |
| `run_prompt` | Low-level method to run any prompt directly through the LLM, used by the `/ai/custom` debug endpoint |

#### `JobQuestionsPipeline` (`services/pipeline.py`)

A secondary agent built with `smolagents.ToolCallingAgent` that has access to the `get_website_content` tool (from `services/scraper.py`). It can fetch and read a company's careers page or job posting URL to enrich the job details before analysis.

---

### Session State Machine

Each resume-building attempt is tracked as a `Session` document whose `ResumeState.stage` progresses through a defined state machine:

```
INIT
  │
  ▼
JOB_ANALYZED          ← POST /ai/analyze
  │
  ▼
REQUIREMENTS_IDENTIFIED  ← POST /ai/compare  (if missing fields found)
  │   or
  └──► READY_FOR_RESUME  ← POST /ai/compare  (if no missing fields)
            ▲
            │
QUESTIONNAIRE_PENDING ← POST /ai/generate-questionnaire
  │  (answer all questions via POST /ai/answer-question)
  └──────────────────────────────────────────────────┘
            │
            ▼
      READY_FOR_RESUME
            │
            ▼
        COMPLETED       ← resume generated
            │  (on error at any stage)
         ERROR
```

Every time an answer is submitted, the agent converts it to structured data and merges it back into the user's Knowledge Graph, keeping the profile permanently up to date.

---

### API Routers

| Router file | Prefix | Key endpoints |
|---|---|---|
| `routers/auth.py` | `/api/v1/auth` | `POST /signup`, `POST /login`, `GET /me`, `POST /logout` |
| `routers/users.py` | `/api/v1/users` | `GET /`, `PUT /`, `POST /knowledge-graph/add`, `GET /knowledge-graph`, `DELETE /knowledge-graph/{category}/{index}` |
| `routers/sessions.py` | `/api/v1/sessions` | `POST /new`, `GET /{session_id}`, `GET /` (list all), `DELETE /{session_id}` |
| `routers/ai.py` | `/api/v1/ai` | `POST /analyze`, `POST /compare`, `POST /generate-questionnaire`, `POST /answer-question`, `POST /answer-questions` (bulk), `POST /parse-text`, `POST /optimize-knowledge-graph`, `POST /custom` |

---

### Utilities

| File | Purpose |
|---|---|
| `utils/auth.py` | `hash_password`, `verify_password`, `create_access_token`, `decode_access_token` |
| `utils/dependencies.py` | `get_current_user` FastAPI dependency – reads JWT from cookie or header and returns the authenticated user |
| `utils/prompt.py` | Centralised LLM prompt templates shared across the agent methods |
| `utils/questions.py` | Helper functions for building and scoring questionnaire items |

---

## Frontend

### Frontend Technology Stack

| Concern | Library / Tool |
|---|---|
| Framework | Next.js 15 (App Router, Turbopack) |
| Language | TypeScript 5 |
| UI primitives | Radix UI (via shadcn/ui) |
| Styling | Tailwind CSS v4 |
| Animations | Framer Motion |
| Forms | React Hook Form + Zod |
| Server state | TanStack Query v5 |
| Client state | Zustand v5 |
| Drag & drop | dnd-kit |
| Print / PDF export | react-to-print |
| Toasts | Sonner |
| Theming | next-themes (dark / light mode) |

---

### Application Routes

The entire application lives under the `(main)` route group, which shares a common layout with a top navigation bar.

| Route | Purpose |
|---|---|
| `/` | Landing / home page with animated hero |
| `/auth/login` | Email + password sign-in |
| `/auth/signup` | New account creation |
| `/resumes` | Lists all of the user's saved resume sessions |
| `/editor` | Multi-step resume editor (accepts optional `?resumeId=` query param) |

---

### Resume Editor Workflow

The editor (`/editor`) is a multi-step wizard driven by `steps.tsx`. Each step corresponds to a form segment:

1. **General Info** – resume title and description.
2. **Personal Info** – name, job title, address, phone, email, social media handles.
3. **Job Description** – target role, company name, website URL, and the job description (text or file upload).
4. **AI Questionnaire** – dynamically generated questions from the backend; the user answers them to fill profile gaps. An `optimize-handler` orchestrates the compare → generate-questionnaire API calls.
5. **Work Experience** – structured entries with position, company, dates, and bulleted description. AI generation dialog available.
6. **Education** – degree, institution, dates, GPA/marks.
7. **Projects** – title, link, dates, description. AI generation dialog available.
8. **Research** – paper title, publication venue, date, URL, description.
9. **Skills** – flat list of skill strings with a searchable selection dialog.

The editor renders a split-panel layout: the left panel contains the active form step, and the right panel (`resume-preview-section.tsx`) shows a live, continuously updated preview of the resume using the `ResumePreview` component. A **Print** button at the top of the preview triggers `react-to-print` for browser-native PDF export.

Breadcrumb navigation at the top of the editor (`bread-crumbs.tsx`) allows the user to jump directly between completed steps.

---

### Component Architecture

```
src/components/
├── resume-preview.tsx      # Renders the formatted, printable resume from ResumeValues
├── sign-in.tsx             # Sign-in form component
├── sign-out.tsx            # Sign-out button component
└── ui/                     # shadcn/ui primitive components
    ├── animated-hero.tsx   # Landing page animated headline
    ├── aurora-background.tsx
    ├── loading-button.tsx  # Button with built-in loading spinner
    ├── text-shimmer.tsx
    ├── theme-toggle.tsx    # Dark / light mode switch
    └── ...                 # Standard Radix-based components (button, card, dialog, etc.)
```

The editor forms each follow the `EditorFormProps` interface, receiving `resumeData` (the full `ResumeValues` object) and a `setResumeData` setter. This makes every form stateless and testable in isolation.

---

### State & Data Management

- **`ResumeValues`** – the canonical shape of all data in the editor. It is assembled by merging the schemas of every individual step: `GeneralInfoValues`, `PersonalInfoValues`, `JobDescriptionValues`, `QuestionAnswerValues`, `EducationValues`, `ProjectsValues`, `ResearchValues`, `SkillsValues`, and `WorkExperienceValues`.
- **TanStack Query** – manages server-side state for API calls (user profile, sessions, questionnaire generation). Provides caching, background refetching, and optimistic updates.
- **Zustand** – manages lightweight client-side state such as the premium feature modal flag (`usePremiumModal`).
- **Custom Hooks** – `useDebounce` (deferred input), `useDimensions` (responsive preview scaling), `useUnloadWarning` (warns the user about unsaved changes before leaving the editor).

---

### Form Validation

All form schemas are defined in `src/lib/validations.ts` using **Zod** and consumed by React Hook Form via `@hookform/resolvers/zod`. Common patterns:

- `optionalString` – a trimmed string that is allowed to be empty; used for most profile fields.
- Array schemas (educations, projects, etc.) allow the list to be undefined when the step has not been visited yet.
- `authSchema` enforces a valid email format and a minimum password length of 6 characters.

`src/lib/transformers.ts` converts between the frontend `ResumeValues` shape and the backend Knowledge Graph format, ensuring that data flows cleanly in both directions without exposing API structure to UI components.

---

## End-to-End Resume Building Flow

```
1. User signs up / logs in
         │
         ▼
2. User fills in personal info and knowledge graph data
   (education, work experience, projects, skills, etc.)
         │
         ▼
3. User creates a new resume session (POST /sessions/new)
         │
         ▼
4. User enters the target job description in the Editor
         │
         ▼
5. Frontend calls POST /ai/analyze
   → AI extracts job requirements and keywords
   → Session stage: JOB_ANALYZED
         │
         ▼
6. Frontend calls POST /ai/compare
   → AI compares job requirements against user's Knowledge Graph
   → If all required fields are present → stage: READY_FOR_RESUME
   → If fields are missing → stage: REQUIREMENTS_IDENTIFIED
         │
         ▼ (only if missing fields)
7. Frontend calls POST /ai/generate-questionnaire
   → AI generates targeted questions for each missing field
   → Stage: QUESTIONNAIRE_PENDING
         │
         ▼
8. User answers questions in the Questionnaire step
   → Each answer is submitted via POST /ai/answer-question
   → AI parses the answer and updates the Knowledge Graph
   → When all questions answered → stage: READY_FOR_RESUME
         │
         ▼
9. User completes remaining editor steps
   (work experience, education, projects, research, skills)
         │
         ▼
10. Live preview renders the tailored resume in real time
          │
          ▼
11. User prints or exports to PDF via react-to-print
```

---

## Deployment

### Backend

The backend ships with a multi-stage `Dockerfile`:

- **Builder stage** – installs Python 3.13, uses `uv sync --frozen` to produce a clean virtual environment from the locked `uv.lock` file.
- **Runtime stage** – copies only the virtual environment and application code into a slim Python 3.13 image, then runs `uv run app/main.py`.

The container exposes port **8000**. The application can also be run locally with the provided `run.sh` script.

### Frontend

The Next.js frontend is built as a standard Next.js application (`next build`) and served with `next start`. It communicates with the backend via the `NEXT_PUBLIC_API_URL` environment variable.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|---|---|
| `MONGODB_URI` | MongoDB connection string |
| `SECRET_KEY` | JWT signing secret |
| `GEMINI_API_KEY` | Google Gemini API key |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Base URL of the backend API (e.g., `http://localhost:8000`) |
