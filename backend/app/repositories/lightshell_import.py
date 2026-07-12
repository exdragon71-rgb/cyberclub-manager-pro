from collections.abc import Collection
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.lightshell_import import (
    LightShellInventoryImport,
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

    def create_or_update_mapping(
        self,
        db: Session,
        *,
        source_name: str,
        normalized_source_name: str,
        source_category: str,
        product_id: UUID,
    ) -> tuple[
        LightShellProductMapping,
        bool,
    ]:
        statement = select(
            LightShellProductMapping
        ).where(
            LightShellProductMapping
            .normalized_source_name
            == normalized_source_name
        )

        mapping = db.scalar(statement)

        if mapping is not None:
            mapping.source_name = source_name
            mapping.source_category = (
                source_category
            )
            mapping.product_id = product_id

            db.flush()

            return mapping, False

        mapping = LightShellProductMapping(
            source_name=source_name,
            normalized_source_name=(
                normalized_source_name
            ),
            source_category=source_category,
            product_id=product_id,
        )

        db.add(mapping)
        db.flush()

        return mapping, True

    def create_import_record(
        self,
        db: Session,
        *,
        branch: str,
        generated_at: datetime,
        source_filename: str,
        total_items: int,
        matched_items: int,
        created_items: int,
        unresolved_items: int,
    ) -> LightShellInventoryImport:
        import_record = (
            LightShellInventoryImport(
                branch=branch,
                generated_at=generated_at,
                source_filename=source_filename,
                total_items=total_items,
                matched_items=matched_items,
                created_items=created_items,
                unresolved_items=(
                    unresolved_items
                ),
            )
        )

        db.add(import_record)
        db.flush()

        return import_record


lightshell_import_repository = (
    LightShellImportRepository()
)