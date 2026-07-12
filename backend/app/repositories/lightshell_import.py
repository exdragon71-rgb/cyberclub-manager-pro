from collections.abc import Collection

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.lightshell_import import (
    LightShellProductMapping,
)


class LightShellImportRepository:
    def get_mappings_by_normalized_names(
        self,
        db: Session,
        normalized_names: Collection[str],
    ) -> dict[str, LightShellProductMapping]:
        if not normalized_names:
            return {}

        statement = (
            select(LightShellProductMapping)
            .options(
                joinedload(
                    LightShellProductMapping.product
                )
            )
            .where(
                LightShellProductMapping
                .normalized_source_name
                .in_(normalized_names)
            )
        )

        mappings = list(
            db.scalars(statement).all()
        )

        return {
            mapping.normalized_source_name: mapping
            for mapping in mappings
        }


lightshell_import_repository = (
    LightShellImportRepository()
)