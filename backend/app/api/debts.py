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
from app.schemas.debt import (
    DebtCreate,
    DebtRead,
    DebtStatus,
    DebtUpdate,
)
from app.services.debt import (
    DebtNotFoundError,
    DebtValidationError,
    debt_service,
)


router = APIRouter(
    prefix="/debts",
    tags=["Debts"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=list[DebtRead],
    summary="Получить список долгов",
)
def get_debts(
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
    debt_status: DebtStatus | None = Query(
        default=None,
        alias="status",
    ),
):
    return debt_service.get_all(
        db,
        offset=offset,
        limit=limit,
        status=debt_status,
    )


@router.get(
    "/{debt_id}",
    response_model=DebtRead,
    summary="Получить долг по ID",
)
def get_debt(
    debt_id: UUID,
    db: DatabaseSession,
):
    try:
        return debt_service.get_by_id(
            db,
            debt_id,
        )

    except DebtNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "",
    response_model=DebtRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить долг",
)
def create_debt(
    debt_data: DebtCreate,
    db: DatabaseSession,
):
    try:
        return debt_service.create(
            db,
            debt_data,
        )

    except DebtValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.patch(
    "/{debt_id}",
    response_model=DebtRead,
    summary="Изменить долг",
)
def update_debt(
    debt_id: UUID,
    debt_data: DebtUpdate,
    db: DatabaseSession,
):
    try:
        return debt_service.update(
            db,
            debt_id,
            debt_data,
        )

    except DebtNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except DebtValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.post(
    "/{debt_id}/pay",
    response_model=DebtRead,
    summary="Погасить долг",
)
def pay_debt(
    debt_id: UUID,
    db: DatabaseSession,
):
    try:
        return debt_service.mark_paid(
            db,
            debt_id,
        )

    except DebtNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except DebtValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error