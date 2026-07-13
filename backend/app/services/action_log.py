from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.action_log import ActionLog
from app.repositories.action_log import (
    ActionLogRepository,
    action_log_repository,
)


class ActionLogService:
    def __init__(
        self,
        repository: ActionLogRepository,
    ) -> None:
        self.repository = repository

    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        event_type: str | None = None,
        entity_type: str | None = None,
    ) -> list[ActionLog]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
            event_type=event_type,
            entity_type=entity_type,
        )

    def record(
        self,
        db: Session,
        *,
        event_type: str,
        entity_type: str,
        entity_id: UUID | None,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> ActionLog:
        return self.repository.create(
            db,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            message=message,
            details=details,
        )


action_log_service = ActionLogService(
    repository=action_log_repository,
)