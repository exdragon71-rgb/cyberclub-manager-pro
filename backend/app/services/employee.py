from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.employee import (
    EmployeeRepository,
    employee_repository,
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
)
from app.services.action_log import (
    ActionLogService,
    action_log_service,
)


class EmployeeNotFoundError(Exception):
    pass


class EmployeeAlreadyExistsError(Exception):
    pass


class EmployeeValidationError(Exception):
    pass


class EmployeeService:
    def __init__(
        self,
        repository: EmployeeRepository,
        action_log_service: ActionLogService,
    ) -> None:
        self.repository = repository
        self.action_log_service = action_log_service

    @staticmethod
    def _get_log_details(
        employee: Employee,
    ) -> dict[str, Any]:
        return {
            "name": employee.name,
            "is_active": employee.is_active,
        }

    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[Employee]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
            include_inactive=include_inactive,
        )

    def get_by_id(
        self,
        db: Session,
        employee_id: UUID,
    ) -> Employee:
        employee = self.repository.get_by_id(
            db,
            employee_id,
        )

        if employee is None:
            raise EmployeeNotFoundError(
                "Сотрудник не найден."
            )

        return employee

    def create(
        self,
        db: Session,
        employee_data: EmployeeCreate,
    ) -> Employee:
        name = employee_data.name.strip()

        if not name:
            raise EmployeeValidationError(
                "Имя сотрудника не может быть пустым."
            )

        existing_employee = (
            self.repository.get_by_name(
                db,
                name,
            )
        )

        if existing_employee is not None:
            raise EmployeeAlreadyExistsError(
                f"Сотрудник с именем "
                f"'{name}' уже существует."
            )

        normalized_data = (
            employee_data.model_copy(
                update={
                    "name": name,
                }
            )
        )

        try:
            employee = self.repository.create(
                db,
                normalized_data,
            )

            self.action_log_service.record(
                db,
                event_type="employee_created",
                entity_type="employee",
                entity_id=employee.id,
                message=(
                    "Добавлен сотрудник "
                    f"«{employee.name}»."
                ),
                details=self._get_log_details(
                    employee,
                ),
            )

            db.commit()
            db.refresh(employee)

            return employee

        except IntegrityError as error:
            db.rollback()

            raise EmployeeAlreadyExistsError(
                "Сотрудник с таким именем "
                "уже существует."
            ) from error

        except Exception:
            db.rollback()
            raise

    def update(
        self,
        db: Session,
        employee_id: UUID,
        employee_data: EmployeeUpdate,
    ) -> Employee:
        employee = self.get_by_id(
            db,
            employee_id,
        )

        before_details = self._get_log_details(
            employee,
        )

        normalized_updates = {}

        if "name" in employee_data.model_fields_set:
            if employee_data.name is None:
                raise EmployeeValidationError(
                    "Имя сотрудника "
                    "не может быть пустым."
                )

            normalized_name = (
                employee_data.name.strip()
            )

            if not normalized_name:
                raise EmployeeValidationError(
                    "Имя сотрудника "
                    "не может быть пустым."
                )

            existing_employee = (
                self.repository.get_by_name(
                    db,
                    normalized_name,
                )
            )

            if (
                existing_employee is not None
                and existing_employee.id
                != employee.id
            ):
                raise EmployeeAlreadyExistsError(
                    f"Сотрудник с именем "
                    f"'{normalized_name}' "
                    "уже существует."
                )

            normalized_updates["name"] = (
                normalized_name
            )

        normalized_data = (
            employee_data.model_copy(
                update=normalized_updates
            )
        )

        try:
            updated_employee = (
                self.repository.update(
                    db,
                    employee,
                    normalized_data,
                )
            )

            after_details = self._get_log_details(
                updated_employee,
            )

            if before_details != after_details:
                self.action_log_service.record(
                    db,
                    event_type="employee_updated",
                    entity_type="employee",
                    entity_id=updated_employee.id,
                    message=(
                        "Изменён сотрудник "
                        f"«{updated_employee.name}»."
                    ),
                    details={
                        "before": before_details,
                        "after": after_details,
                    },
                )

            db.commit()
            db.refresh(updated_employee)

            return updated_employee

        except IntegrityError as error:
            db.rollback()

            raise EmployeeAlreadyExistsError(
                "Сотрудник с таким именем "
                "уже существует."
            ) from error

        except Exception:
            db.rollback()
            raise

    def archive(
        self,
        db: Session,
        employee_id: UUID,
    ) -> Employee:
        employee = self.get_by_id(
            db,
            employee_id,
        )

        if not employee.is_active:
            return employee

        archive_data = EmployeeUpdate(
            is_active=False,
        )

        try:
            archived_employee = (
                self.repository.update(
                    db,
                    employee,
                    archive_data,
                )
            )

            self.action_log_service.record(
                db,
                event_type="employee_archived",
                entity_type="employee",
                entity_id=archived_employee.id,
                message=(
                    "Сотрудник "
                    f"«{archived_employee.name}» "
                    "перенесён в архив."
                ),
                details={
                    "name": archived_employee.name,
                    "is_active": False,
                },
            )

            db.commit()
            db.refresh(archived_employee)

            return archived_employee

        except Exception:
            db.rollback()
            raise

    def restore(
        self,
        db: Session,
        employee_id: UUID,
    ) -> Employee:
        employee = self.get_by_id(
            db,
            employee_id,
        )

        if employee.is_active:
            return employee

        restore_data = EmployeeUpdate(
            is_active=True,
        )

        try:
            restored_employee = (
                self.repository.update(
                    db,
                    employee,
                    restore_data,
                )
            )

            self.action_log_service.record(
                db,
                event_type="employee_restored",
                entity_type="employee",
                entity_id=restored_employee.id,
                message=(
                    "Сотрудник "
                    f"«{restored_employee.name}» "
                    "восстановлен из архива."
                ),
                details={
                    "name": restored_employee.name,
                    "is_active": True,
                },
            )

            db.commit()
            db.refresh(restored_employee)

            return restored_employee

        except Exception:
            db.rollback()
            raise


employee_service = EmployeeService(
    repository=employee_repository,
    action_log_service=action_log_service,
)