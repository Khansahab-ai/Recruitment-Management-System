
from fastapi import FastAPI, Depends
from app.core.config import settings
from sqlmodel import Session, SQLModel
from sqlalchemy import text
from app.db.session import get_session, engine
from app.models import Department, JobRequisition
from app import models
from app.api.v1.router import api_router

print("REGISTERED TABLES:", sorted(SQLModel.metadata.tables.keys()))

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="End-to-End Recruitment Management System"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix="/api/v1"
)

@app.get("/")
def root():
    return {
        "message": "Recruitment Management System API",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend"
    }

@app.get("/health/database")
def database_health(
    session: Session = Depends(get_session)
):
    session.exec(text("SELECT 1"))

    return {"status": "connected"}

@app.on_event("startup")
def create_db_tables():
    SQLModel.metadata.create_all(engine)

    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
        )

        print("DATABASE TABLES:", [row[0] for row in result])