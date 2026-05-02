# repositories/maintenance_repository.py
from typing import List, Optional

from models.maintenance import MaintenanceTask
from repositories.base_repository import BaseRepository


class MaintenanceRepository(BaseRepository):
    def list_all(self) -> List[MaintenanceTask]:
        rows = self._fetch_all(
            "SELECT * FROM maintenance_tasks ORDER BY created_at DESC"
        )
        return [MaintenanceTask.from_row(r) for r in rows]

    def get(self, task_id: int) -> Optional[MaintenanceTask]:
        row = self._fetch_one(
            "SELECT * FROM maintenance_tasks WHERE id = ?", (task_id,)
        )
        return MaintenanceTask.from_row(row) if row else None

    def create(self, task: MaintenanceTask) -> int:
        return self._execute(
            """INSERT INTO maintenance_tasks (asset_name, asset_type, priority,
                                               assigned_employee_id, status, description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (task.asset_name, task.asset_type, task.priority,
             task.assigned_employee_id, task.status, task.description),
        )

    def update(self, task: MaintenanceTask) -> None:
        self._execute(
            """UPDATE maintenance_tasks
                  SET asset_name=?, asset_type=?, priority=?, assigned_employee_id=?,
                      status=?, description=?
                WHERE id=?""",
            (task.asset_name, task.asset_type, task.priority,
             task.assigned_employee_id, task.status, task.description, task.id),
        )

    def delete(self, task_id: int) -> None:
        self._execute("DELETE FROM maintenance_tasks WHERE id = ?", (task_id,))
