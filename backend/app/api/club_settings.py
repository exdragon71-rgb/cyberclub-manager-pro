from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.club_setting import (
    ClubSettingRead,
    ClubSettingUpdate,
)
from app.services.club_setting import (
    ClubSettingValidationError,
    club_setting_service,
)


router = APIRouter(
    prefix="/club-settings",
    tags=["Club Settings"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=ClubSettingRead,
    summary="Получить настройки клуба",
)
def get_club_settings(
    db: DatabaseSession,
):
    return club_setting_service.get_default(
        db,
    )


@router.patch(
    "",
    response_model=ClubSettingRead,
    summary="Изменить настройки клуба",
)
def update_club_settings(
    setting_data: ClubSettingUpdate,
    db: DatabaseSession,
):
    try:
        return club_setting_service.update(
            db,
            setting_data,
        )

    except ClubSettingValidationError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error