from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlalchemy import text

from app.db.session import get_session

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Recruitment Management API",
        "version": "v1"
    }


@router.get("/database-health")
def database_health(
    session: Session = Depends(get_session)
):
    try:
        session.exec(text("SELECT 1")).first()

        return {
            "status": "connected",
            "database": "PostgreSQL"
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(error)}"
        )