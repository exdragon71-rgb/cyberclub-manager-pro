from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeRepository:
    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[Employee]:
        statement = select(Employee).order_by(
            Employee.name
        )

        if not include_inactive:
            statement = statement.where(
                Employee.is_active.is_(True)
            )

        statement = statement.offset(offset).limit(limit)

        return list(
            db.scalars(statement).all()
        )

    def get_by_id(
        self,
        db: Session,
        employee_id: UUID,
    ) -> Employee | None:
        statement = select(Employee).where(
            Employee.id == employee_id
        )

        return db.scalar(statement)

    def get_by_name(
        self,
        db: Session,
        name: str,
    ) -> Employee | None:
        normalized_name = name.strip().lower()

        statement = select(Employee).where(
            func.lower(Employee.name)
            == normalized_name
        )

        return db.scalar(statement)

    def create(
        self,
        db: Session,
        employee_data: EmployeeCreate,
    ) -> Employee:
        employee = Employee(
            name=employee_data.name.strip(),
        )

        db.add(employee)
        db.flush()

        return employee

    def update(
        self,
        db: Session,
        employee: Employee,
        employee_data: EmployeeUpdate,
    ) -> Employee:
        update_data = employee_data.model_dump(
            exclude_unset=True
        )

        if "name" in update_data:
            update_data["name"] = (
                update_data["name"].strip()
            )

        for field_name, field_value in update_data.items():
            setattr(
                employee,
                field_name,
                field_value,
            )

        db.flush()

        return employee


employee_repository = EmployeeRepository()