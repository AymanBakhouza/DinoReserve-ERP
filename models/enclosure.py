# models/enclosure.py

from dataclasses import dataclass

from models.base import Entity


@dataclass
class Enclosure(Entity):
    name: str = ""
    zone_type: str = ""
    max_capacity: int = 1
    current_capacity: int = 0
    fence_voltage: float = 0.0
    security_level: int = 1
    status: str = "active"

    def occupancy_ratio(self) -> float:
        """Devuelve el ratio de ocupación entre 0 y 1."""
        if self.max_capacity <= 0:
            return 0.0
        return self.current_capacity / self.max_capacity

    def display_name(self) -> str:
        return f"{self.name} [{self.zone_type}]"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "zone_type": self.zone_type,
            "max_capacity": self.max_capacity,
            "current_capacity": self.current_capacity,
            "fence_voltage": self.fence_voltage,
            "security_level": self.security_level,
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row) -> "Enclosure":
        return cls(
            id=row["id"],
            name=row["name"],
            zone_type=row["zone_type"],
            max_capacity=row["max_capacity"],
            current_capacity=row["current_capacity"],
            fence_voltage=row["fence_voltage"],
            security_level=row["security_level"],
            status=row["status"],
            created_at=row["created_at"],
        )
