from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.prize import (
    PrizeCreate,
    PrizeRead,
    PrizeStatus,
    PrizeUpdate,
)
from app.services.prize import (
    PrizeNotFoundError,
    PrizeValidationError,
    prize_service,
)


router = APIRouter(
    prefix="/prizes",
    tags=["Prizes"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=list[PrizeRead],
    summary="Получить список лотерейных призов",
)
def get_prizes(
    db: DatabaseSession,
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    prize_status: PrizeStatus | None = Query(
        default=None,
        alias="status",
    ),
):
    return prize_service.get_all(
        db,
        offset=offset,
        limit=limit,
        status=prize_status,
    )


@router.get(
    "/{prize_id}",
    response_model=PrizeRead,
    summary="Получить лотерейный приз по ID",
)
def get_prize(
    prize_id: UUID,
    db: DatabaseSession,
):
    try:
        return prize_service.get_by_id(
            db,
            prize_id,
        )

    except PrizeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "",
    response_model=PrizeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить выданный лотерейный приз",
)
def create_prize(
    prize_data: PrizeCreate,
    db: DatabaseSession,
):
    try:
        return prize_service.create(
            db,
            prize_data,
        )

    except PrizeValidationError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error


@router.patch(
    "/{prize_id}",
    response_model=PrizeRead,
    summary="Изменить лотерейный приз",
)
def update_prize(
    prize_id: UUID,
    prize_data: PrizeUpdate,
    db: DatabaseSession,
):
    try:
        return prize_service.update(
            db,
            prize_id,
            prize_data,
        )

    except PrizeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except PrizeValidationError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error


@router.post(
    "/{prize_id}/confirm-reflected",
    response_model=PrizeRead,
    summary="Подтвердить учёт приза в LightShell",
)
def confirm_prize_reflected(
    prize_id: UUID,
    db: DatabaseSession,
):
    try:
        return prize_service.mark_written_off(
            db,
            prize_id,
        )

    except PrizeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except PrizeValidationError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error