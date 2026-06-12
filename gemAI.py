from fastapi import FastAPI
from google import genai
import os
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


app = FastAPI()


@app.post("/response")
def get_response(message: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=message,
    )
    return response.text


@app.post("/stream")
def get_response_stream(message: str) -> str:
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=message,
    )

    def generate():
        for stream in response:
            if stream.text:
                yield stream.text
    return StreamingResponse(generate(), media_type="text/plain")
