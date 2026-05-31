from fastapi import FastAPI
from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()


@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/message")
def getResponse(message: str) -> str:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=message,
    )
    return response.text
