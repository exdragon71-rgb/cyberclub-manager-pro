from collections import defaultdict
from decimal import Decimal

from sqlalchemy.orm import Session

from app.integrations.lightshell.normalization import (
    normalize_lightshell_name,
)
from app.integrations.lightshell.schemas import (
    LightShellImportApplyResult,
    LightShellImportPreview,
    LightShellImportPreviewItem,
    LightShellImportResolution,
    LightShellInventoryDocument,
    LightShellMatchStatus,
    LightShellResolutionAction,
)
from app.models.product import Product
from app.repositories.inventory_balance import (
    inventory_balance_repository,
)
from app.repositories.lightshell_import import (
    lightshell_import_repository,
)
from app.repositories.product import product_repository
from app.schemas.product import ProductCreate
from app.services.action_log import (
    ActionLogService,
    action_log_service,
)
from app.services.product import product_service


class LightShellImportValidationError(Exception):
    pass


class LightShellImportService:
    def __init__(
        self,
        action_log_service: ActionLogService,
    ) -> None:
        self.action_log_service = action_log_service

    def build_preview(
        self,
        db: Session,
        *,
        document: LightShellInventoryDocument,
        source_filename: str,
    ) -> LightShellImportPreview:
        products = (
            product_repository.get_all_for_matching(
                db,
            )
        )

        products_by_normalized_name: dict[
            str,
            list[Product],
        ] = defaultdict(list)

        for product in products:
            normalized_product_name = (
                normalize_lightshell_name(
                    product.name
                )
            )

            products_by_normalized_name[
                normalized_product_name
            ].append(product)

        normalized_source_names = {
            normalize_lightshell_name(
                item.name
            )
            for item in document.items
        }

        mappings = (
            lightshell_import_repository
            .get_mappings_by_normalized_names(
                db,
                normalized_source_names,
            )
        )

        preview_items: list[
            LightShellImportPreviewItem
        ] = []

        matched_items = 0
        unmatched_items = 0
        ambiguous_items = 0

        for item in document.items:
            normalized_source_name = (
                normalize_lightshell_name(
                    item.name
                )
            )

            mapping = mappings.get(
                normalized_source_name
            )

            if (
                mapping is not None
                and mapping.product.is_active
            ):
                status = (
                    LightShellMatchStatus.MAPPED
                )

                product_id = mapping.product.id
                product_name = mapping.product.name
                matched_items += 1

            else:
                matching_products = (
                    products_by_normalized_name.get(
                        normalized_source_name,
                        [],
                    )
                )

                if len(matching_products) == 1:
                    matched_product = (
                        matching_products[0]
                    )

                    status = (
                        LightShellMatchStatus.EXACT
                    )

                    product_id = matched_product.id
                    product_name = (
                        matched_product.name
                    )
                    matched_items += 1

                elif len(matching_products) > 1:
                    status = (
                        LightShellMatchStatus.AMBIGUOUS
                    )

                    product_id = None
                    product_name = None
                    ambiguous_items += 1

                else:
                    status = (
                        LightShellMatchStatus.UNMATCHED
                    )

                    product_id = None
                    product_name = None
                    unmatched_items += 1

            preview_items.append(
                LightShellImportPreviewItem(
                    source_number=(
                        item.source_number
                    ),
                    source_name=item.name,
                    normalized_source_name=(
                        normalized_source_name
                    ),
                    source_category=item.category,
                    program_quantity=(
                        item.program_quantity
                    ),
                    status=status,
                    product_id=product_id,
                    product_name=product_name,
                )
            )

        return LightShellImportPreview(
            branch=document.branch,
            generated_at=document.generated_at,
            source_filename=(
                source_filename.strip()
            ),
            total_items=len(
                preview_items
            ),
            matched_items=matched_items,
            unmatched_items=unmatched_items,
            ambiguous_items=ambiguous_items,
            items=preview_items,
        )

    def apply_import(
        self,
        db: Session,
        *,
        document: LightShellInventoryDocument,
        source_filename: str,
        resolutions: list[
            LightShellImportResolution
        ],
    ) -> LightShellImportApplyResult:
        normalized_filename = (
            source_filename.strip()
        )

        if not normalized_filename:
            raise LightShellImportValidationError(
                "Название исходного файла "
                "не может быть пустым."
            )

        document_items = {
            item.source_number: item
            for item in document.items
        }

        resolutions_by_number: dict[
            int,
            LightShellImportResolution,
        ] = {}

        for resolution in resolutions:
            source_number = (
                resolution.source_number
            )

            if source_number in resolutions_by_number:
                raise LightShellImportValidationError(
                    "Для позиции №"
                    f"{source_number} передано "
                    "несколько решений."
                )

            if source_number not in document_items:
                raise LightShellImportValidationError(
                    "В PDF отсутствует позиция №"
                    f"{source_number}."
                )

            resolutions_by_number[
                source_number
            ] = resolution

        missing_numbers = sorted(
            set(document_items)
            - set(resolutions_by_number)
        )

        if missing_numbers:
            missing_text = ", ".join(
                str(number)
                for number in missing_numbers[:10]
            )

            if len(missing_numbers) > 10:
                missing_text += ", ..."

            raise LightShellImportValidationError(
                "Не указано решение для позиций: "
                f"{missing_text}."
            )

        resolved_products: dict[
            int,
            Product,
        ] = {}

        used_product_ids = set()

        created_products = 0
        skipped_items = 0
        created_mappings = 0
        updated_items = 0

        changed_program_quantities: list[
            dict[str, object]
        ] = []

        try:
            for item in document.items:
                resolution = (
                    resolutions_by_number[
                        item.source_number
                    ]
                )

                if (
                    resolution.action
                    == LightShellResolutionAction.SKIP
                ):
                    skipped_items += 1
                    continue

                if (
                    resolution.action
                    == (
                        LightShellResolutionAction
                        .USE_EXISTING
                    )
                ):
                    if resolution.product_id is None:
                        raise (
                            LightShellImportValidationError(
                                "Для позиции №"
                                f"{item.source_number} "
                                "не указан товар."
                            )
                        )

                    product = (
                        product_repository.get_by_id(
                            db,
                            resolution.product_id,
                        )
                    )

                    if product is None:
                        raise (
                            LightShellImportValidationError(
                                "Товар для позиции №"
                                f"{item.source_number} "
                                "не найден."
                            )
                        )

                    if not product.is_active:
                        raise (
                            LightShellImportValidationError(
                                "Товар для позиции №"
                                f"{item.source_number} "
                                "находится в архиве."
                            )
                        )

                elif (
                    resolution.action
                    == (
                        LightShellResolutionAction
                        .CREATE_NEW
                    )
                ):
                    product = (
                        product_service
                        .create_in_transaction(
                            db,
                            ProductCreate(
                                name=item.name,
                                price=Decimal("0"),
                                unit="шт.",
                                minimum_stock=(
                                    Decimal("0")
                                ),
                                lightshell_id=None,
                            ),
                        )
                    )

                    created_products += 1

                else:
                    raise (
                        LightShellImportValidationError(
                            "Неизвестное действие "
                            "для позиции №"
                            f"{item.source_number}."
                        )
                    )

                if product.id in used_product_ids:
                    raise (
                        LightShellImportValidationError(
                            "Один товар приложения "
                            "нельзя связать сразу "
                            "с несколькими позициями PDF."
                        )
                    )

                used_product_ids.add(
                    product.id
                )

                resolved_products[
                    item.source_number
                ] = product

            balances = (
                inventory_balance_repository
                .get_by_product_ids(
                    db,
                    {
                        product.id
                        for product
                        in resolved_products.values()
                    },
                )
            )

            for item in document.items:
                product = resolved_products.get(
                    item.source_number
                )

                if product is None:
                    continue

                balance = balances.get(
                    product.id
                )

                if balance is None:
                    raise (
                        LightShellImportValidationError(
                            "Для товара "
                            f"«{product.name}» "
                            "не найдены остатки."
                        )
                    )

                program_quantity_before = (
                    balance.program_quantity
                )

                (
                    inventory_balance_repository
                    .update_program_quantity(
                        db,
                        balance,
                        item.program_quantity,
                    )
                )

                if (
                    program_quantity_before
                    != item.program_quantity
                ):
                    changed_program_quantities.append(
                        {
                            "source_number": (
                                item.source_number
                            ),
                            "source_name": (
                                item.name
                            ),
                            "product_id": str(
                                product.id
                            ),
                            "product_name": (
                                product.name
                            ),
                            "before": str(
                                program_quantity_before
                            ),
                            "after": str(
                                item.program_quantity
                            ),
                        }
                    )

                normalized_source_name = (
                    normalize_lightshell_name(
                        item.name
                    )
                )

                (
                    _,
                    mapping_was_created,
                ) = (
                    lightshell_import_repository
                    .create_or_update_mapping(
                        db,
                        source_name=item.name,
                        normalized_source_name=(
                            normalized_source_name
                        ),
                        source_category=(
                            item.category
                        ),
                        product_id=product.id,
                    )
                )

                if mapping_was_created:
                    created_mappings += 1

                updated_items += 1

            import_record = (
                lightshell_import_repository
                .create_import_record(
                    db,
                    branch=document.branch,
                    generated_at=(
                        document.generated_at
                    ),
                    source_filename=(
                        normalized_filename
                    ),
                    total_items=len(
                        document.items
                    ),
                    matched_items=(
                        updated_items
                        - created_products
                    ),
                    created_items=(
                        created_products
                    ),
                    unresolved_items=(
                        skipped_items
                    ),
                )
            )

            self.action_log_service.record(
                db,
                event_type=(
                    "lightshell_import_applied"
                ),
                entity_type="lightshell_import",
                entity_id=import_record.id,
                message=(
                    "Выполнен импорт LightShell "
                    f"из файла "
                    f"«{normalized_filename}»."
                ),
                details={
                    "branch": (
                        import_record.branch
                    ),
                    "generated_at": (
                        import_record
                        .generated_at
                        .isoformat()
                        if import_record.generated_at
                        else None
                    ),
                    "source_filename": (
                        import_record
                        .source_filename
                    ),
                    "total_items": (
                        import_record.total_items
                    ),
                    "updated_items": (
                        updated_items
                    ),
                    "created_products": (
                        created_products
                    ),
                    "skipped_items": (
                        skipped_items
                    ),
                    "created_mappings": (
                        created_mappings
                    ),
                    "changed_items": len(
                        changed_program_quantities
                    ),
                    "changed_program_quantities": (
                        changed_program_quantities
                    ),
                },
            )

            db.commit()
            db.refresh(import_record)

            return LightShellImportApplyResult(
                import_id=import_record.id,
                branch=import_record.branch,
                generated_at=(
                    import_record.generated_at
                ),
                source_filename=(
                    import_record.source_filename
                ),
                total_items=(
                    import_record.total_items
                ),
                updated_items=updated_items,
                created_products=(
                    created_products
                ),
                skipped_items=skipped_items,
                created_mappings=(
                    created_mappings
                ),
            )

        except Exception:
            db.rollback()
            raise


lightshell_import_service = (
    LightShellImportService(
        action_log_service=action_log_service,
    )
)