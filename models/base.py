# models/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Entity(ABC):
    """Entidad base. Toda entidad del dominio expone id y created_at."""

    id: Optional[int] = field(default=None)
    created_at: Optional[str] = field(default=None)

    @abstractmethod
    def to_dict(self) -> dict:
        """Serializa la entidad a un diccionario plano (para repositorios)."""

    @abstractmethod
    def display_name(self) -> str:
        """Texto humano descriptivo de la entidad (para listados/logs)."""
