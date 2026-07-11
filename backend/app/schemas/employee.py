from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EmployeeBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
        examples=["Рома"],
    )


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    is_active: bool | None = None


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime