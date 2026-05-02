# models/maintenance.py
from dataclasses import dataclass
from typing import Optional

from models.base import Entity


@dataclass
class MaintenanceTask(Entity):
    asset_name: str = ""
    asset_type: str = ""
    priority: str = "medium"
    assigned_employee_id: Optional[int] = None
    status: str = "pending"
    description: str = ""

    def display_name(self) -> str:
        return f"{self.asset_name} ({self.asset_type}) — {self.status}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
            "priority": self.priority,
            "assigned_employee_id": self.assigned_employee_id,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row) -> "MaintenanceTask":
        return cls(
            id=row["id"],
            asset_name=row["asset_name"],
            asset_type=row["asset_type"],
            priority=row["priority"],
            assigned_employee_id=row["assigned_employee_id"],
            status=row["status"],
            description=row["description"] or "",
            created_at=row["created_at"],
        )
