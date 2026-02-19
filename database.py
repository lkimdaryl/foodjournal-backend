from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Load environment variables (if using .env file)
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/postgres'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()