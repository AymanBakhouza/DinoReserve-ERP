# services/enclosure_service.py
# Servicio de lógica de negocio para recintos.

from typing import List

from models.enclosure import Enclosure
from repositories.enclosure_repository import EnclosureRepository
from utils.constants import ENCLOSURE_STATUSES
from utils.exceptions import (
    CapacityExceededError,
    FenceSecurityError,
    ValidationError,
)
from utils.logger import get_logger
from utils.validators import (
    require_in_options,
    require_int_in_range,
    require_non_empty,
    require_positive_number,
)


class EnclosureService:
    def __init__(self):
        self._repo = EnclosureRepository()
        self._log = get_logger()

    def list_all(self) -> List[Enclosure]:
        return self._repo.list_all()

    def _validate(self, data: dict) -> dict:
        max_cap = require_int_in_range(
            data.get("max_capacity"), "capacidad máxima", 1, 100
        )
        cur_cap = require_int_in_range(
            data.get("current_capacity", 0), "capacidad actual", 0, 100
        )
        if cur_cap > max_cap:
            raise CapacityExceededError(
                "La capacidad actual no puede exceder la máxima."
            )
        voltage = require_positive_number(
            data.get("fence_voltage", 0), "voltaje de valla", allow_zero=True
        )
        if voltage > 50000:
            raise FenceSecurityError("Voltaje de valla fuera de rango (0-50000).")
        return {
            "name": require_non_empty(data.get("name"), "nombre"),
            "zone_type": require_non_empty(data.get("zone_type"), "tipo de zona"),
            "max_capacity": max_cap,
            "current_capacity": cur_cap,
            "fence_voltage": voltage,
            "security_level": require_int_in_range(
                data.get("security_level"), "nivel de seguridad", 1, 5
            ),
            "status": require_in_options(
                data.get("status"), "estado", ENCLOSURE_STATUSES
            ),
        }

    def create(self, data: dict) -> int:
        clean = self._validate(data)
        new_id = self._repo.create(Enclosure(**clean))
        self._log.info("Recinto creado id=%s nombre=%s", new_id, clean["name"])
        return new_id

    def update(self, enc_id: int, data: dict) -> None:
        clean = self._validate(data)
        if self._repo.get(enc_id) is None:
            raise ValidationError("Recinto no encontrado.")
        self._repo.update(Enclosure(id=enc_id, **clean))
        self._log.info("Recinto actualizado id=%s", enc_id)

    def delete(self, enc_id: int) -> None:
        self._repo.delete(enc_id)
        self._log.info("Recinto eliminado id=%s", enc_id)
