from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api import (
    debts_router,
    employees_router,
    inventory_balances_router,
    lightshell_imports_router,
    products_router,
)
from app.core.config import settings
from app.core.database import engine


app = FastAPI(
    title=settings.app_name,
    description="Backend API for CyberClub Manager Pro",
    version=settings.app_version,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(products_router)
app.include_router(inventory_balances_router)
app.include_router(employees_router)
app.include_router(debts_router)
app.include_router(lightshell_imports_router)


@app.get(
    "/",
    tags=["System"],
    summary="Информация о приложении",
)
def root():
    return {
        "app": "CyberClub Manager Pro",
        "version": settings.app_version,
        "status": "running",
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Проверка backend",
)
def health_check():
    return {
        "status": "ok",
    }


@app.get(
    "/health/database",
    tags=["System"],
    summary="Проверка PostgreSQL",
)
def database_health_check():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT 1")
            )
            result.scalar_one()

        return {
            "status": "ok",
            "database": settings.db_name,
            "user": settings.db_user,
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from error