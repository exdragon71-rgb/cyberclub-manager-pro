from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import engine


app = FastAPI(
    title=settings.app_name,
    description="Backend API for CyberClub Manager Pro",
    version=settings.app_version,
)


@app.get("/", tags=["System"])
def root():
    return {
        "app": "CyberClub Manager Pro",
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
    }


@app.get("/health/database", tags=["System"])
def database_health_check():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.scalar_one()

        return {
            "status": "ok",
            "database": settings.db_name,
            "user": settings.db_user,
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )