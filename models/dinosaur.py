# models/dinosaur.py
from dataclasses import dataclass, field
from typing import Optional

from models.base import Entity


@dataclass
class Dinosaur(Entity):
    """Dinosaurio genérico. Implementa el método polimórfico calculate_risk_level()."""

    name: str = ""
    species: str = ""
    diet_type: str = "omnivore"           # carnivore | herbivore | omnivore
    danger_level: int = 1                 # 1..5
    health_status: str = "healthy"        # healthy | observation | sick | critical
    enclosure_id: Optional[int] = None
    feeding_level: int = 100              # 0..100

    # ---- Polimorfismo ----
    def calculate_risk_level(self) -> int:
        """Riesgo base: combina danger_level con salud y alimentación."""
        risk = self.danger_level
        if self.health_status == "sick":
            risk += 1
        if self.health_status == "critical":
            risk += 2
        if self.feeding_level < 40:
            risk += 1
        return max(1, min(10, risk))

    def display_name(self) -> str:
        return f"{self.name} ({self.species})"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "diet_type": self.diet_type,
            "danger_level": self.danger_level,
            "health_status": self.health_status,
            "enclosure_id": self.enclosure_id,
            "feeding_level": self.feeding_level,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row) -> "Dinosaur":
        """Construye la subclase apropiada según diet_type."""
        diet = row["diet_type"]
        if diet == "carnivore":
            klass = CarnivoreDinosaur
        elif diet == "herbivore":
            klass = HerbivoreDinosaur
        else:
            klass = cls
        return klass(
            id=row["id"],
            name=row["name"],
            species=row["species"],
            diet_type=row["diet_type"],
            danger_level=row["danger_level"],
            health_status=row["health_status"],
            enclosure_id=row["enclosure_id"],
            feeding_level=row["feeding_level"],
            created_at=row["created_at"],
        )


@dataclass
class CarnivoreDinosaur(Dinosaur):
    """Carnívoro: riesgo elevado por defecto."""
    diet_type: str = "carnivore"

    def calculate_risk_level(self) -> int:
        risk = super().calculate_risk_level()
        # Los carnívoros añaden +2 al riesgo base.
        return min(10, risk + 2)


@dataclass
class HerbivoreDinosaur(Dinosaur):
    """Herbívoro: riesgo reducido."""
    diet_type: str = "herbivore"

    def calculate_risk_level(self) -> int:
        risk = super().calculate_risk_level()
        return max(1, risk - 1)
