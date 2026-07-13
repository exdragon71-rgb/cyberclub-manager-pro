from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ActionLogRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    event_type: str
    entity_type: str
    entity_id: UUID | None

    message: str

    details: dict[str, Any]

    created_at: datetime