from fastapi import FastAPI, HTTPException
from google import genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class List(BaseModel):
    text: str = None
    is_done: bool = False


app = FastAPI()


items = []
lists = []


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


@app.post("/items")
def create_item(item: str):
    items.append(item)
    return


@app.get("/items")
def get_item_list(limit: int = 10) -> list[str]:
    return items[0:limit]


@app.get("/items/{item_id}")
def get_item(item_id: int) -> str:
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail="Invalid item id")


@app.post("/add_item")
def todo(item: List):
    lists.append(item)


@app.get("/get_item")
def todo_get(num: int = 10):
    return lists[0:num]

@app.put("/items/{}")








