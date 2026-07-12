from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[Product]:
        statement = select(Product).order_by(
            Product.name
        )

        if not include_inactive:
            statement = statement.where(
                Product.is_active.is_(True)
            )

        statement = statement.offset(
            offset
        ).limit(
            limit
        )

        return list(
            db.scalars(statement).all()
        )

    def get_all_for_matching(
        self,
        db: Session,
        *,
        include_inactive: bool = False,
    ) -> list[Product]:
        statement = select(Product).order_by(
            Product.name
        )

        if not include_inactive:
            statement = statement.where(
                Product.is_active.is_(True)
            )

        return list(
            db.scalars(statement).all()
        )

    def get_by_id(
        self,
        db: Session,
        product_id: UUID,
    ) -> Product | None:
        statement = select(Product).where(
            Product.id == product_id
        )

        return db.scalar(statement)

    def get_by_name(
        self,
        db: Session,
        name: str,
    ) -> Product | None:
        normalized_name = name.strip().lower()

        statement = select(Product).where(
            func.lower(Product.name)
            == normalized_name
        )

        return db.scalar(statement)

    def get_by_lightshell_id(
        self,
        db: Session,
        lightshell_id: str,
    ) -> Product | None:
        normalized_id = lightshell_id.strip()

        statement = select(Product).where(
            Product.lightshell_id
            == normalized_id
        )

        return db.scalar(statement)

    def create(
        self,
        db: Session,
        product_data: ProductCreate,
    ) -> Product:
        product = Product(
            name=product_data.name.strip(),
            price=product_data.price,
            unit=product_data.unit.strip(),
            minimum_stock=(
                product_data.minimum_stock
            ),
            lightshell_id=(
                product_data.lightshell_id.strip()
                if product_data.lightshell_id
                else None
            ),
        )

        db.add(product)
        db.flush()

        return product

    def update(
        self,
        db: Session,
        product: Product,
        product_data: ProductUpdate,
    ) -> Product:
        update_data = product_data.model_dump(
            exclude_unset=True
        )

        if "name" in update_data:
            update_data["name"] = (
                update_data["name"].strip()
            )

        if "unit" in update_data:
            update_data["unit"] = (
                update_data["unit"].strip()
            )

        if "lightshell_id" in update_data:
            lightshell_id = update_data[
                "lightshell_id"
            ]

            update_data["lightshell_id"] = (
                lightshell_id.strip()
                if lightshell_id
                else None
            )

        for (
            field_name,
            field_value,
        ) in update_data.items():
            setattr(
                product,
                field_name,
                field_value,
            )

        db.flush()

        return product


product_repository = ProductRepository()