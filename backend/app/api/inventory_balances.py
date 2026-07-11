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
from app.schemas.inventory_balance import (
    InventoryBalanceRead,
    InventoryBalanceUpdate,
)
from app.services.inventory_balance import (
    InventoryBalanceNotFoundError,
    inventory_balance_service,
)


router = APIRouter(
    prefix="/inventory-balances",
    tags=["Inventory Balances"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=list[InventoryBalanceRead],
    summary="Получить остатки товаров",
)
def get_inventory_balances(
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
    return inventory_balance_service.get_all(
        db,
        offset=offset,
        limit=limit,
        include_inactive=include_inactive,
    )


@router.get(
    "/{product_id}",
    response_model=InventoryBalanceRead,
    summary="Получить остатки товара",
)
def get_inventory_balance(
    product_id: UUID,
    db: DatabaseSession,
):
    try:
        return inventory_balance_service.get_by_product_id(
            db,
            product_id,
        )

    except InventoryBalanceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch(
    "/{product_id}",
    response_model=InventoryBalanceRead,
    summary="Изменить остатки товара",
)
def update_inventory_balance(
    product_id: UUID,
    balance_data: InventoryBalanceUpdate,
    db: DatabaseSession,
):
    try:
        return inventory_balance_service.update(
            db,
            product_id,
            balance_data,
        )

    except InventoryBalanceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error