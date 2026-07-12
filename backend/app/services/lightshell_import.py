from collections import defaultdict

from sqlalchemy.orm import Session

from app.integrations.lightshell.normalization import (
    normalize_lightshell_name,
)
from app.integrations.lightshell.schemas import (
    LightShellImportPreview,
    LightShellImportPreviewItem,
    LightShellInventoryDocument,
    LightShellMatchStatus,
)
from app.models.product import Product
from app.repositories.lightshell_import import (
    lightshell_import_repository,
)
from app.repositories.product import product_repository


class LightShellImportService:
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


lightshell_import_service = (
    LightShellImportService()
)