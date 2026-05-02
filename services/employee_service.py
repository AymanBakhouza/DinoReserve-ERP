# services/employee_service.py
# Servicio de lógica de negocio para empleados.
from typing import List

from models.employee import Employee
from repositories.employee_repository import EmployeeRepository
from utils.constants import EMPLOYEE_ROLES, EMPLOYEE_STATUSES
from utils.exceptions import ValidationError
from utils.logger import get_logger
from utils.validators import (
    require_in_options,
    require_int_in_range,
    require_non_empty,
    require_positive_number,
)


class EmployeeService:
    def __init__(self):
        self._repo = EmployeeRepository()
        self._log = get_logger()

    def list_all(self) -> List[Employee]:
        return self._repo.list_all()

    def _validate(self, data: dict) -> dict:
        zone = data.get("assigned_zone")
        if zone in (None, "", 0):
            zone = None
        else:
            zone = int(zone)
        return {
            "name": require_non_empty(data.get("name"), "nombre"),
            "role": require_in_options(data.get("role"), "rol", EMPLOYEE_ROLES),
            "salary": require_positive_number(
                data.get("salary"), "salario", allow_zero=False
            ),
            "assigned_zone": zone,
            "technical_level": require_int_in_range(
                data.get("technical_level"), "nivel técnico", 1, 5
            ),
            "status": require_in_options(
                data.get("status"), "estado", EMPLOYEE_STATUSES
            ),
        }

    def create(self, data: dict) -> int:
        clean = self._validate(data)
        new_id = self._repo.create(Employee(**clean))
        self._log.info("Empleado creado id=%s", new_id)
        return new_id

    def update(self, emp_id: int, data: dict) -> None:
        clean = self._validate(data)
        if self._repo.get(emp_id) is None:
            raise ValidationError("Empleado no encontrado.")
        self._repo.update(Employee(id=emp_id, **clean))
        self._log.info("Empleado actualizado id=%s", emp_id)

    def delete(self, emp_id: int) -> None:
        self._repo.delete(emp_id)
        self._log.info("Empleado eliminado id=%s", emp_id)
