from fastapi import FastAPI
from services.gemini_client import gemini_client
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    response = gemini_client.generate_content(
        "Give me a cheeky one line ping message for my API. Only give me the message, no other text."
    )
    return {"message": f"{response}"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)