from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.club_setting import ClubSetting
from app.repositories.club_setting import (
    ClubSettingRepository,
    club_setting_repository,
)
from app.schemas.club_setting import (
    ClubSettingUpdate,
)
from app.services.action_log import (
    ActionLogService,
    action_log_service,
)


class ClubSettingValidationError(Exception):
    pass


class ClubSettingService:
    def __init__(
        self,
        repository: ClubSettingRepository,
        action_log_service: ActionLogService,
    ) -> None:
        self.repository = repository
        self.action_log_service = action_log_service

    @staticmethod
    def _get_log_details(
        club_setting: ClubSetting,
    ) -> dict[str, Any]:
        return {
            "club_name": club_setting.club_name,
            "branch": club_setting.branch,
            "lottery_ticket_price": format(
                club_setting.lottery_ticket_price,
                ".2f",
            ),
        }

    def get_default(
        self,
        db: Session,
    ) -> ClubSetting:
        club_setting = (
            self.repository.get_default(
                db,
            )
        )

        if club_setting is not None:
            return club_setting

        try:
            club_setting = (
                self.repository.create_default(
                    db,
                )
            )

            db.commit()
            db.refresh(club_setting)

            return club_setting

        except IntegrityError:
            db.rollback()

            club_setting = (
                self.repository.get_default(
                    db,
                )
            )

            if club_setting is None:
                raise

            return club_setting

        except Exception:
            db.rollback()
            raise

    def update(
        self,
        db: Session,
        setting_data: ClubSettingUpdate,
    ) -> ClubSetting:
        club_setting = self.get_default(
            db,
        )

        before_details = (
            self._get_log_details(
                club_setting,
            )
        )

        normalized_updates = {}

        if (
            "club_name"
            in setting_data.model_fields_set
        ):
            if setting_data.club_name is None:
                raise ClubSettingValidationError(
                    "Название клуба "
                    "не может быть пустым."
                )

            normalized_club_name = (
                setting_data.club_name.strip()
            )

            if not normalized_club_name:
                raise ClubSettingValidationError(
                    "Название клуба "
                    "не может быть пустым."
                )

            normalized_updates[
                "club_name"
            ] = normalized_club_name

        if (
            "branch"
            in setting_data.model_fields_set
        ):
            if setting_data.branch is None:
                raise ClubSettingValidationError(
                    "Название филиала "
                    "не может быть пустым."
                )

            normalized_branch = (
                setting_data.branch.strip()
            )

            if not normalized_branch:
                raise ClubSettingValidationError(
                    "Название филиала "
                    "не может быть пустым."
                )

            normalized_updates[
                "branch"
            ] = normalized_branch

        normalized_data = (
            setting_data.model_copy(
                update=normalized_updates,
            )
        )

        try:
            updated_setting = (
                self.repository.update(
                    db,
                    club_setting,
                    normalized_data,
                )
            )

            after_details = (
                self._get_log_details(
                    updated_setting,
                )
            )

            if before_details != after_details:
                self.action_log_service.record(
                    db,
                    event_type=(
                        "club_setting_updated"
                    ),
                    entity_type=(
                        "club_setting"
                    ),
                    entity_id=(
                        updated_setting.id
                    ),
                    message=(
                        "Изменены настройки клуба."
                    ),
                    details={
                        "before": before_details,
                        "after": after_details,
                    },
                )

            db.commit()
            db.refresh(updated_setting)

            return updated_setting

        except Exception:
            db.rollback()
            raise


club_setting_service = ClubSettingService(
    repository=club_setting_repository,
    action_log_service=action_log_service,
)