from fastapi import FastAPI
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()


items = []


@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/message")
def get_response(message: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=message,
    )
    return response.text


@app.get("/items")
def item(item: str) -> list[str]:
    items.append(item)
    return items
