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
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeRead,
    EmployeeUpdate,
)
from app.services.employee import (
    EmployeeAlreadyExistsError,
    EmployeeNotFoundError,
    EmployeeValidationError,
    employee_service,
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=list[EmployeeRead],
    summary="Получить список сотрудников",
)
def get_employees(
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
    include_inactive: bool = Query(
        default=False,
    ),
):
    return employee_service.get_all(
        db,
        offset=offset,
        limit=limit,
        include_inactive=include_inactive,
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeRead,
    summary="Получить сотрудника по ID",
)
def get_employee(
    employee_id: UUID,
    db: DatabaseSession,
):
    try:
        return employee_service.get_by_id(
            db,
            employee_id,
        )

    except EmployeeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить сотрудника",
)
def create_employee(
    employee_data: EmployeeCreate,
    db: DatabaseSession,
):
    try:
        return employee_service.create(
            db,
            employee_data,
        )

    except EmployeeAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except EmployeeValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error


@router.patch(
    "/{employee_id}",
    response_model=EmployeeRead,
    summary="Изменить сотрудника",
)
def update_employee(
    employee_id: UUID,
    employee_data: EmployeeUpdate,
    db: DatabaseSession,
):
    try:
        return employee_service.update(
            db,
            employee_id,
            employee_data,
        )

    except EmployeeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except EmployeeAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except EmployeeValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error


@router.post(
    "/{employee_id}/archive",
    response_model=EmployeeRead,
    summary="Переместить сотрудника в архив",
)
def archive_employee(
    employee_id: UUID,
    db: DatabaseSession,
):
    try:
        return employee_service.archive(
            db,
            employee_id,
        )

    except EmployeeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/{employee_id}/restore",
    response_model=EmployeeRead,
    summary="Восстановить сотрудника из архива",
)
def restore_employee(
    employee_id: UUID,
    db: DatabaseSession,
):
    try:
        return employee_service.restore(
            db,
            employee_id,
        )

    except EmployeeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error