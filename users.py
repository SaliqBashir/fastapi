from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


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
def create_item(user: User):
    for existing_user in users:
        if existing_user.id == user.id:
            raise HTTPException(
                status_code=400,
                detail="User ID already exists"
            )
    users.append(user)
    return user


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, new_user: UserUpdate):
    for user in users:
        if user_id == user.id:
            user.age = new_user.age
            user.email = new_user.email
            return user
    raise HTTPException(status_code=404, detail="Invalid user id")


@app.patch("/users/{user_id}", response_model=User)
def patch_user(user_id: int, patch: UserPatch):
    for user in users:
        if user_id == user.id:
            user.email = patch.email
            return user
    raise HTTPException(status_code=404, detail="Invalid user id")


@app.delete("/users/{user_id}", response_model=None, status_code=204)
def delete_user(user_id: int):
    for i, user in enumerate(users):
        if user_id == user.id:
            users.pop(i)
            return None
    raise HTTPException(status_code=404, detail="Invalid user id")
