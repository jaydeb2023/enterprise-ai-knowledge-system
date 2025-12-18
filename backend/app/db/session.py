from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# FORCE LOCAL SQLITE (ignore env completely)
DATABASE_URL = "sqlite:///./enterprise.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
