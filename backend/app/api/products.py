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
from app.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from app.services.product import (
    ProductAlreadyExistsError,
    ProductNotFoundError,
    ProductValidationError,
    product_service,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=list[ProductRead],
    summary="Получить список товаров",
)
def get_products(
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
    return product_service.get_all(
        db,
        offset=offset,
        limit=limit,
        include_inactive=include_inactive,
    )


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Получить товар по ID",
)
def get_product(
    product_id: UUID,
    db: DatabaseSession,
):
    try:
        return product_service.get_by_id(
            db,
            product_id,
        )

    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить товар",
)
def create_product(
    product_data: ProductCreate,
    db: DatabaseSession,
):
    try:
        return product_service.create(
            db,
            product_data,
        )

    except ProductAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except ProductValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    summary="Изменить товар",
)
def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: DatabaseSession,
):
    try:
        return product_service.update(
            db,
            product_id,
            product_data,
        )

    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ProductAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except ProductValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.post(
    "/{product_id}/archive",
    response_model=ProductRead,
    summary="Переместить товар в архив",
)
def archive_product(
    product_id: UUID,
    db: DatabaseSession,
):
    try:
        return product_service.archive(
            db,
            product_id,
        )

    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/{product_id}/restore",
    response_model=ProductRead,
    summary="Восстановить товар из архива",
)
def restore_product(
    product_id: UUID,
    db: DatabaseSession,
):
    try:
        return product_service.restore(
            db,
            product_id,
        )

    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error