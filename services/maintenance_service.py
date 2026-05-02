# services/maintenance_service.py
# Servicio de lógica de negocio para tareas de mantenimiento.


from typing import List

from models.maintenance import MaintenanceTask
from repositories.maintenance_repository import MaintenanceRepository
from utils.constants import MAINTENANCE_PRIORITIES, MAINTENANCE_STATUSES
from utils.exceptions import ValidationError
from utils.logger import get_logger
from utils.validators import require_in_options, require_non_empty


class MaintenanceService:
    def __init__(self):
        self._repo = MaintenanceRepository()
        self._log = get_logger()

    def list_all(self) -> List[MaintenanceTask]:
        return self._repo.list_all()

    def _validate(self, data: dict) -> dict:
        emp = data.get("assigned_employee_id")
        if emp in (None, "", 0):
            emp = None
        else:
            emp = int(emp)
        return {
            "asset_name": require_non_empty(data.get("asset_name"), "nombre del activo"),
            "asset_type": require_non_empty(data.get("asset_type"), "tipo de activo"),
            "priority": require_in_options(
                data.get("priority"), "prioridad", MAINTENANCE_PRIORITIES
            ),
            "assigned_employee_id": emp,
            "status": require_in_options(
                data.get("status"), "estado", MAINTENANCE_STATUSES
            ),
            "description": (data.get("description") or "").strip(),
        }

    def create(self, data: dict) -> int:
        clean = self._validate(data)
        new_id = self._repo.create(MaintenanceTask(**clean))
        self._log.info("Tarea de mantenimiento creada id=%s", new_id)
        if clean["priority"] in ("high", "critical"):
            self._log.warning(
                "MANTENIMIENTO PRIORIDAD %s — '%s'",
                clean["priority"].upper(), clean["asset_name"],
            )
        return new_id

    def update(self, task_id: int, data: dict) -> None:
        clean = self._validate(data)
        if self._repo.get(task_id) is None:
            raise ValidationError("Tarea no encontrada.")
        self._repo.update(MaintenanceTask(id=task_id, **clean))
        self._log.info("Tarea de mantenimiento actualizada id=%s", task_id)

    def delete(self, task_id: int) -> None:
        self._repo.delete(task_id)
        self._log.info("Tarea de mantenimiento eliminada id=%s", task_id)
