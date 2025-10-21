# Resume Maker Backend

## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)

## Running the App

## Using Docker

1. Install docker

2. Pull the docker image
   ```bash
   docker pull sohamghugare/resume-maker-backend:latest

   # Or pull this for x86-64 architecture
   docker pull sohamghugare/resume-maker-backend-amd:latest
   ```

3. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. Run the docker image
   ```bash
   docker run --rm -it -p 8000:8000 --env-file .env sohamghugare/resume-maker-backend:latest
   ```

## Using UV

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. Run the development server:
   ```bash
   uv run app/main.py
   ```

The API will be available at `http://127.0.0.1:8000`