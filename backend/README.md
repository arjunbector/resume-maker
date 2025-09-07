# Resume Maker Backend

## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)

## Running the App

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