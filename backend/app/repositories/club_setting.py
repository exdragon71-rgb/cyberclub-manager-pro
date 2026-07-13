from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.club_setting import ClubSetting
from app.schemas.club_setting import ClubSettingUpdate


DEFAULT_SETTING_KEY = "default"


class ClubSettingRepository:
    def get_default(
        self,
        db: Session,
    ) -> ClubSetting | None:
        statement = select(
            ClubSetting
        ).where(
            ClubSetting.setting_key
            == DEFAULT_SETTING_KEY
        )

        return db.scalar(statement)

    def create_default(
        self,
        db: Session,
    ) -> ClubSetting:
        club_setting = ClubSetting(
            setting_key=DEFAULT_SETTING_KEY,
        )

        db.add(club_setting)
        db.flush()

        return club_setting

    def update(
        self,
        db: Session,
        club_setting: ClubSetting,
        setting_data: ClubSettingUpdate,
    ) -> ClubSetting:
        update_data = (
            setting_data.model_dump(
                exclude_unset=True,
            )
        )

        if "club_name" in update_data:
            update_data["club_name"] = (
                update_data[
                    "club_name"
                ].strip()
            )

        if "branch" in update_data:
            update_data["branch"] = (
                update_data[
                    "branch"
                ].strip()
            )

        for (
            field_name,
            field_value,
        ) in update_data.items():
            setattr(
                club_setting,
                field_name,
                field_value,
            )

        db.flush()

        return club_setting


club_setting_repository = (
    ClubSettingRepository()
)