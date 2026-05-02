# models/employee.py

from dataclasses import dataclass
from typing import Optional

from models.base import Entity


@dataclass
class Employee(Entity):
    name: str = ""
    role: str = ""
    salary: float = 0.0
    assigned_zone: Optional[int] = None
    technical_level: int = 1
    status: str = "active"

    def display_name(self) -> str:
        return f"{self.name} — {self.role}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "salary": self.salary,
            "assigned_zone": self.assigned_zone,
            "technical_level": self.technical_level,
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row) -> "Employee":
        return cls(
            id=row["id"],
            name=row["name"],
            role=row["role"],
            salary=row["salary"],
            assigned_zone=row["assigned_zone"],
            technical_level=row["technical_level"],
            status=row["status"],
            created_at=row["created_at"],
        )
