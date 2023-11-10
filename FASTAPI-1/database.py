from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pymongo import MongoClient
from pydantic import BaseModel

URL_DATABASE = 'postgresql://postgres:amal1998!@localhost:5432/userRegistration'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["user_profiles"]