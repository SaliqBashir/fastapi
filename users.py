from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import time
from functools import wraps
from fastapi.responses import JSONResponse


class User(BaseModel):
    id: int
    age: int
    email: str


class UserUpdate(BaseModel):
    age: int
    email: str


class UserPatch(BaseModel):
    email: str


users = []
app = FastAPI()
requests = {}


def require_auth(func):
    @wraps(func)
    def wrapper(*args, request: Request, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if api_key != "secret123":
            raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )
        return func(*args, request=request, **kwargs)
    return wrapper


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip = request.client.host
    current_time = time.time()
    if ip not in requests:
        requests[ip] = []
    requests[ip] = [
        timestamp
        for timestamp in requests[ip]
        if current_time - timestamp < 60
    ]
    if len(requests[ip]) > 5:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests."}
        )
    requests[ip].append(current_time)
    return await call_next(request)


@app.get("/")
def root():
    return {"Hello, World"}


@app.get("/users", response_model=list[User])
def get_users():
    return users


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users:
        if user_id == user.id:
            return user
    raise HTTPException(status_code=404, detail="Invalid user id")


@app.post("/users", response_model=User, status_code=201)
@require_auth
def create_item(user: User, request: Request):
    for existing_user in users:
        if existing_user.id == user.id:
            raise HTTPException(
                status_code=400,
                detail="User ID already exists"
            )
    users.append(user)
    return user


@app.put("/users/{user_id}", response_model=User)
@require_auth
def update_user(user_id: int, new_user: UserUpdate, request: Request):
    for user in users:
        if user_id == user.id:
            user.age = new_user.age
            user.email = new_user.email
            return user
    raise HTTPException(status_code=404, detail="Invalid user id")


@app.patch("/users/{user_id}", response_model=User)
@require_auth
def patch_user(user_id: int, patch: UserPatch, request: Request):
    for user in users:
        if user_id == user.id:
            user.email = patch.email
            return user
    raise HTTPException(status_code=404, detail="Invalid user id")


@app.delete("/users/{user_id}", response_model=None, status_code=204)
@require_auth
def delete_user(user_id: int, request: Request):
    for i, user in enumerate(users):
        if user_id == user.id:
            users.pop(i)
            return None
    raise HTTPException(status_code=404, detail="Invalid user id")
