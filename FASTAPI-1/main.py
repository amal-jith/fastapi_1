from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Annotated
from database import engine, SessionLocal, mongo_db
import models
from sqlalchemy.orm import Session, sessionmaker

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

SessionPostgreSQL = sessionmaker(autocommit=False, autoflush=False, bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    full_name: str
    password: str    email: str
    phone: str
    profile_picture: str


class UserRegistration(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str


class UserDetails(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    profile_picture: str



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/register", response_model=UserDetails)
async def register_user(user: UserRegistration, existing_user=None):
    db_postgres = SessionPostgreSQL()
    existing_user = db_postgres.query(models.UserPostgreSQL).filter(models.UserPostgreSQL.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_postgres.add(models.UserPostgreSQL(**user.dict()))
    db_postgres.commit()
    db_postgres.refresh(existing_user)
    db_postgres.close()

    profile_picture = {"user_id": existing_user.id, "profile_picture": user.profile_picture}
    mongo_db["profile_pictures"].insert_one(profile_picture)

    return UserDetails(id=existing_user.id, full_name=user.full_name, email=user.email, phone=user.phone, profile_picture=user.profile_picture )



@app.get("/user/{user_id}", response_model=UserDetails)
async def get_user_details(user_id: int, token: str = Depends(oauth2_scheme)):
    db_postgres = SessionPostgreSQL()
    user_postgres = db_postgres.query(models.UserPostgreSQL).filter(models.UserPostgreSQL.id == user_id).first()
    db_postgres.close()

    if not user_postgres:
        raise HTTPException(status_code=404, detail="User not found")

    profile_picture = mongo_db["profile_pictures"].find_one({"user_id": user_id})
    profile_picture_url = profile_picture["profile_picture"] if profile_picture else None

    return UserDetails(id=user_postgres.id, full_name=user_postgres.full_name, email=user_postgres.email, phone=user_postgres.phone, profile_picture=profile_picture_url)