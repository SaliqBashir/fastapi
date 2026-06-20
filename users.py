from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
import time
from functools import wraps
from fastapi.responses import JSONResponse
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session


class User(BaseModel):
    id: int
    age: int
    email: str


class UserUpdate(BaseModel):
    age: int
    email: str


class UserPatch(BaseModel):
    email: str


class UserCreate(BaseModel):
    age: int
    email: str


app = FastAPI()
requests = {}
models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


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
    print(ip)
    current_time = time.time()
    if ip not in requests:
        requests[ip] = []
    requests[ip] = [
        timestamp
        for timestamp in requests[ip]
        if current_time - timestamp < 60
    ]
    if len(requests[ip]) >= 100:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests."}
        )
    requests[ip].append(current_time)
    return await call_next(request)


@app.get("/users", response_model=list[User], status_code=200)
def get_users(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


@app.get("/users/{user_id}", response_model=User, status_code=200)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user_model = (
        db.query(models.Users)
        .filter(models.Users.id == user_id)
        .first()
    )

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid user id"
        )

    return user_model


@app.post("/users", response_model=User, status_code=201)
@require_auth
def create_item(
        user: UserCreate,
        request: Request,
        db: Session = Depends(get_db)
):
    user_model = models.Users()
    user_model.age = user.age
    user_model.email = user.email
    db.add(user_model)
    db.commit()
    return user_model


@app.put("/users/{user_id}", response_model=User, status_code=200)
@require_auth
def update_user(
        user_id: int,
        new_user: UserUpdate,
        request: Request,
        db: Session = Depends(get_db)
):
    user_model = db.query(
        models.Users).filter(
        models.Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="Invalid user id")
    user_model.age = new_user.age
    user_model.email = new_user.email
    db.commit()
    db.refresh(user_model)
    return user_model


@app.patch("/users/{user_id}", response_model=User, status_code=200)
@require_auth
def patch_user(
        user_id: int,
        patch: UserPatch,
        request: Request,
        db: Session = Depends(get_db)
):
    user_model = db.query(
        models.Users).filter(
        models.Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="Invalid user id")
    user_model.email = patch.email
    db.commit()
    db.refresh(user_model)
    return user_model


@app.delete("/users/{user_id}", status_code=204)
@require_auth
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user_model = (
        db.query(models.Users)
        .filter(models.Users.id == user_id)
        .first()
    )

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid user id"
        )

    db.delete(user_model)
    db.commit()
