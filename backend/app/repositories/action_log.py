from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.action_log import ActionLog


class ActionLogRepository:
    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        event_type: str | None = None,
        entity_type: str | None = None,
    ) -> list[ActionLog]:
        statement = (
            select(ActionLog)
            .order_by(
                ActionLog.created_at.desc(),
            )
        )

        if event_type is not None:
            statement = statement.where(
                ActionLog.event_type
                == event_type
            )

        if entity_type is not None:
            statement = statement.where(
                ActionLog.entity_type
                == entity_type
            )

        statement = statement.offset(
            offset,
        ).limit(
            limit,
        )

        return list(
            db.scalars(
                statement,
            ).all(),
        )

    def create(
        self,
        db: Session,
        *,
        event_type: str,
        entity_type: str,
        entity_id: UUID | None,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> ActionLog:
        action_log = ActionLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            message=message,
            details=details or {},
        )

        db.add(
            action_log,
        )

        db.flush()

        return action_log


action_log_repository = ActionLogRepository()