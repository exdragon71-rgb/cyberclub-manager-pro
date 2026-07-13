from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.action_log import ActionLogRead
from app.services.action_log import action_log_service


router = APIRouter(
    prefix="/action-logs",
    tags=["Action Logs"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=list[ActionLogRead],
    summary="Получить журнал действий",
)
def get_action_logs(
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
    event_type: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    entity_type: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
):
    return action_log_service.get_all(
        db,
        offset=offset,
        limit=limit,
        event_type=event_type,
        entity_type=entity_type,
    )