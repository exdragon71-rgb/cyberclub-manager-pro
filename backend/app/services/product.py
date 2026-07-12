from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.inventory_balance import (
    InventoryBalanceRepository,
    inventory_balance_repository,
)
from app.repositories.product import (
    ProductRepository,
    product_repository,
)
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
)


class ProductNotFoundError(Exception):
    pass


class ProductAlreadyExistsError(Exception):
    pass


class ProductValidationError(Exception):
    pass


class ProductService:
    def __init__(
        self,
        repository: ProductRepository,
        balance_repository: InventoryBalanceRepository,
    ) -> None:
        self.repository = repository
        self.balance_repository = balance_repository

    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[Product]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
            include_inactive=include_inactive,
        )

    def get_by_id(
        self,
        db: Session,
        product_id: UUID,
    ) -> Product:
        product = self.repository.get_by_id(
            db,
            product_id,
        )

        if product is None:
            raise ProductNotFoundError(
                "Товар не найден."
            )

        return product

    def create_in_transaction(
        self,
        db: Session,
        product_data: ProductCreate,
    ) -> Product:
        name = product_data.name.strip()
        unit = product_data.unit.strip()

        lightshell_id = (
            product_data.lightshell_id.strip()
            if product_data.lightshell_id
            else None
        )

        if not name:
            raise ProductValidationError(
                "Название товара не может быть пустым."
            )

        if not unit:
            raise ProductValidationError(
                "Единица измерения не может быть пустой."
            )

        existing_product = (
            self.repository.get_by_name(
                db,
                name,
            )
        )

        if existing_product is not None:
            raise ProductAlreadyExistsError(
                f"Товар с названием "
                f"'{name}' уже существует."
            )

        if lightshell_id is not None:
            existing_lightshell_product = (
                self.repository
                .get_by_lightshell_id(
                    db,
                    lightshell_id,
                )
            )

            if (
                existing_lightshell_product
                is not None
            ):
                raise ProductAlreadyExistsError(
                    "Товар с таким LightShell ID "
                    "уже существует."
                )

        normalized_data = (
            product_data.model_copy(
                update={
                    "name": name,
                    "unit": unit,
                    "lightshell_id": (
                        lightshell_id
                    ),
                }
            )
        )

        product = self.repository.create(
            db,
            normalized_data,
        )

        self.balance_repository.create_for_product(
            db,
            product.id,
        )

        return product

    def create(
        self,
        db: Session,
        product_data: ProductCreate,
    ) -> Product:
        try:
            product = self.create_in_transaction(
                db,
                product_data,
            )

            db.commit()
            db.refresh(product)

            return product

        except IntegrityError as error:
            db.rollback()

            raise ProductAlreadyExistsError(
                "Не удалось создать товар: "
                "название или LightShell ID "
                "уже используются."
            ) from error

        except Exception:
            db.rollback()
            raise

    def update(
        self,
        db: Session,
        product_id: UUID,
        product_data: ProductUpdate,
    ) -> Product:
        product = self.get_by_id(
            db,
            product_id,
        )

        normalized_updates = {}

        if "name" in product_data.model_fields_set:
            if product_data.name is None:
                raise ProductValidationError(
                    "Название товара "
                    "не может быть пустым."
                )

            normalized_name = (
                product_data.name.strip()
            )

            if not normalized_name:
                raise ProductValidationError(
                    "Название товара "
                    "не может быть пустым."
                )

            existing_product = (
                self.repository.get_by_name(
                    db,
                    normalized_name,
                )
            )

            if (
                existing_product is not None
                and existing_product.id
                != product.id
            ):
                raise ProductAlreadyExistsError(
                    f"Товар с названием "
                    f"'{normalized_name}' "
                    "уже существует."
                )

            normalized_updates["name"] = (
                normalized_name
            )

        if "unit" in product_data.model_fields_set:
            if product_data.unit is None:
                raise ProductValidationError(
                    "Единица измерения "
                    "не может быть пустой."
                )

            normalized_unit = (
                product_data.unit.strip()
            )

            if not normalized_unit:
                raise ProductValidationError(
                    "Единица измерения "
                    "не может быть пустой."
                )

            normalized_updates["unit"] = (
                normalized_unit
            )

        if (
            "lightshell_id"
            in product_data.model_fields_set
        ):
            normalized_lightshell_id = (
                product_data.lightshell_id.strip()
                if product_data.lightshell_id
                else None
            )

            if (
                normalized_lightshell_id
                is not None
            ):
                existing_lightshell_product = (
                    self.repository
                    .get_by_lightshell_id(
                        db,
                        normalized_lightshell_id,
                    )
                )

                if (
                    existing_lightshell_product
                    is not None
                    and (
                        existing_lightshell_product.id
                        != product.id
                    )
                ):
                    raise ProductAlreadyExistsError(
                        "Товар с таким "
                        "LightShell ID уже существует."
                    )

            normalized_updates[
                "lightshell_id"
            ] = normalized_lightshell_id

        normalized_data = (
            product_data.model_copy(
                update=normalized_updates
            )
        )

        try:
            updated_product = (
                self.repository.update(
                    db,
                    product,
                    normalized_data,
                )
            )

            db.commit()
            db.refresh(updated_product)

            return updated_product

        except IntegrityError as error:
            db.rollback()

            raise ProductAlreadyExistsError(
                "Не удалось изменить товар: "
                "название или LightShell ID "
                "уже используются."
            ) from error

        except Exception:
            db.rollback()
            raise

    def archive(
        self,
        db: Session,
        product_id: UUID,
    ) -> Product:
        product = self.get_by_id(
            db,
            product_id,
        )

        if not product.is_active:
            return product

        archive_data = ProductUpdate(
            is_active=False
        )

        try:
            archived_product = (
                self.repository.update(
                    db,
                    product,
                    archive_data,
                )
            )

            db.commit()
            db.refresh(archived_product)

            return archived_product

        except Exception:
            db.rollback()
            raise

    def restore(
        self,
        db: Session,
        product_id: UUID,
    ) -> Product:
        product = self.get_by_id(
            db,
            product_id,
        )

        if product.is_active:
            return product

        restore_data = ProductUpdate(
            is_active=True
        )

        try:
            restored_product = (
                self.repository.update(
                    db,
                    product,
                    restore_data,
                )
            )

            db.commit()
            db.refresh(restored_product)

            return restored_product

        except Exception:
            db.rollback()
            raise


product_service = ProductService(
    repository=product_repository,
    balance_repository=(
        inventory_balance_repository
    ),
)