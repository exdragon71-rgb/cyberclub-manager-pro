from pathlib import Path
import sys

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api import (
    action_logs_router,
    booking_notes_router,
    club_settings_router,
    debts_router,
    employees_router,
    inventory_balances_router,
    lightshell_imports_router,
    prizes_router,
    products_router,
)
from app.core.config import settings
from app.core.database import engine


def get_resource_root() -> Path:
    if getattr(
        sys,
        "frozen",
        False,
    ):
        return Path(
            sys._MEIPASS,
        )

    return (
        Path(__file__)
        .resolve()
        .parents[2]
    )


RESOURCE_ROOT = get_resource_root()

FRONTEND_DIST = (
    RESOURCE_ROOT
    / "frontend"
    / "dist"
)

FRONTEND_INDEX = (
    FRONTEND_DIST
    / "index.html"
)

API_ROOT_PATHS = {
    "api",
    "health",
    "products",
    "inventory-balances",
    "employees",
    "debts",
    "prizes",
    "lightshell-imports",
    "action-logs",
    "club-settings",
    "booking-notes",
}


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API for "
        "CyberClub Manager Pro"
    ),
    version=settings.app_version,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(products_router)
app.include_router(
    inventory_balances_router,
)
app.include_router(employees_router)
app.include_router(debts_router)
app.include_router(prizes_router)
app.include_router(
    lightshell_imports_router,
)
app.include_router(action_logs_router)
app.include_router(
    club_settings_router,
)
app.include_router(
    booking_notes_router,
)


@app.get(
    "/api/info",
    tags=["System"],
    summary="Информация о приложении",
)
def application_info():
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
            detail=(
                "Database connection failed"
            ),
        ) from error


if (
    FRONTEND_DIST.is_dir()
    and (
        FRONTEND_DIST
        / "assets"
    ).is_dir()
):
    app.mount(
        "/assets",
        StaticFiles(
            directory=(
                FRONTEND_DIST
                / "assets"
            ),
        ),
        name="frontend-assets",
    )


def request_accepts_html(
    request: Request,
) -> bool:
    accept_header = (
        request.headers.get(
            "accept",
            "",
        )
    )

    return (
        "text/html"
        in accept_header
    )


@app.get(
    "/",
    include_in_schema=False,
)
def serve_root(
    request: Request,
):
    if (
        request_accepts_html(
            request,
        )
        and FRONTEND_INDEX.is_file()
    ):
        return FileResponse(
            FRONTEND_INDEX,
        )

    return {
        "app": "CyberClub Manager Pro",
        "version": settings.app_version,
        "status": "running",
    }


@app.get(
    "/{full_path:path}",
    include_in_schema=False,
)
def serve_frontend_route(
    full_path: str,
    request: Request,
):
    first_path_part = (
        full_path
        .split("/", 1)[0]
    )

    if (
        first_path_part
        in API_ROOT_PATHS
    ):
        raise HTTPException(
            status_code=404,
            detail="Not Found",
        )

    if not request_accepts_html(
        request,
    ):
        raise HTTPException(
            status_code=404,
            detail="Not Found",
        )

    requested_file = (
        FRONTEND_DIST
        / full_path
    ).resolve()

    frontend_dist_resolved = (
        FRONTEND_DIST.resolve()
    )

    if (
        requested_file.is_relative_to(
            frontend_dist_resolved,
        )
        and requested_file.is_file()
    ):
        return FileResponse(
            requested_file,
        )

    if FRONTEND_INDEX.is_file():
        return FileResponse(
            FRONTEND_INDEX,
        )

    raise HTTPException(
        status_code=404,
        detail=(
            "Frontend build not found."
        ),
    )
