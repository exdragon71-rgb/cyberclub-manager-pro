from functools import lru_cache
from pathlib import Path
import sys

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


def get_env_file_path() -> Path:
    if getattr(
        sys,
        "frozen",
        False,
    ):
        return (
            Path(
                sys.executable,
            ).resolve().parent
            / ".env"
        )

    return (
        Path(__file__)
        .resolve()
        .parents[2]
        / ".env"
    )


class Settings(BaseSettings):
    app_name: str = (
        "CyberClub Manager Pro API"
    )

    app_version: str = "0.1.0"

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    model_config = SettingsConfigDict(
        env_file=str(
            get_env_file_path(),
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            "postgresql+psycopg2://"
            f"{self.db_user}:"
            f"{self.db_password}@"
            f"{self.db_host}:"
            f"{self.db_port}/"
            f"{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
