from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # fallback for quick local run (SQLite). For production, set DATABASE_URL explicitly.
    DATABASE_URL = "sqlite:///./test.db"

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, pool_pre_ping=True)
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    # Ensure tables are created before first request.
    # Import models lazily to avoid circular import issues at module import.
    from models import Driver, Disabled, Car, DriveRequest, ShopRequest, Review
    Base.metadata.create_all(bind=engine)


init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
