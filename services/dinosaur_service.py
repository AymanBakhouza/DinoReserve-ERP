# services/dinosaur_service.py
# Servicio de lógica de negocio para dinosaurios.
from typing import List

from models.dinosaur import Dinosaur
from repositories.dinosaur_repository import DinosaurRepository
from repositories.enclosure_repository import EnclosureRepository
from utils.constants import DIET_TYPES, HEALTH_STATUSES
from utils.exceptions import CapacityExceededError, ValidationError
from utils.logger import get_logger
from utils.validators import (
    require_in_options,
    require_int_in_range,
    require_non_empty,
)


class DinosaurService:
    def __init__(self):
        self._repo = DinosaurRepository()
        self._enc_repo = EnclosureRepository()
        self._log = get_logger()

    def list_all(self) -> List[Dinosaur]:
        return self._repo.list_all()

    def _validate(self, data: dict) -> dict:
        cleaned = {
            "name": require_non_empty(data.get("name"), "nombre"),
            "species": require_non_empty(data.get("species"), "especie"),
            "diet_type": require_in_options(
                data.get("diet_type"), "dieta", DIET_TYPES
            ),
            "danger_level": require_int_in_range(
                data.get("danger_level"), "nivel de peligro", 1, 5
            ),
            "health_status": require_in_options(
                data.get("health_status"), "salud", HEALTH_STATUSES
            ),
            "feeding_level": require_int_in_range(
                data.get("feeding_level", 100), "alimentación", 0, 100
            ),
            "enclosure_id": data.get("enclosure_id"),
        }
        if cleaned["enclosure_id"] in (None, "", 0):
            cleaned["enclosure_id"] = None
        else:
            cleaned["enclosure_id"] = int(cleaned["enclosure_id"])
        return cleaned

    def _check_capacity(self, enclosure_id, ignore_dino_id=None):
        if enclosure_id is None:
            return
        enc = self._enc_repo.get(enclosure_id)
        if enc is None:
            raise ValidationError("El recinto seleccionado no existe.")
        current = self._repo.count_by_enclosure(enclosure_id)
        if ignore_dino_id is not None:
            existing = self._repo.get(ignore_dino_id)
            if existing and existing.enclosure_id == enclosure_id:
                current -= 1
        if current + 1 > enc.max_capacity:
            raise CapacityExceededError(
                f"El recinto '{enc.name}' está lleno ({enc.max_capacity} máx)."
            )

    def create(self, data: dict) -> int:
        clean = self._validate(data)
        self._check_capacity(clean["enclosure_id"])
        dino = Dinosaur(**clean)
        new_id = self._repo.create(dino)
        self._refresh_enclosure_capacity(clean["enclosure_id"])
        self._log.info("Dinosaurio creado id=%s nombre=%s", new_id, dino.name)
        return new_id

    def update(self, dino_id: int, data: dict) -> None:
        clean = self._validate(data)
        self._check_capacity(clean["enclosure_id"], ignore_dino_id=dino_id)
        original = self._repo.get(dino_id)
        if original is None:
            raise ValidationError("Dinosaurio no encontrado.")
        dino = Dinosaur(id=dino_id, **clean)
        self._repo.update(dino)
        # recalcular ocupación de recintos involucrados
        for eid in {original.enclosure_id, clean["enclosure_id"]}:
            self._refresh_enclosure_capacity(eid)
        self._log.info("Dinosaurio actualizado id=%s", dino_id)

    def delete(self, dino_id: int) -> None:
        original = self._repo.get(dino_id)
        if original is None:
            return
        self._repo.delete(dino_id)
        self._refresh_enclosure_capacity(original.enclosure_id)
        self._log.info("Dinosaurio eliminado id=%s", dino_id)

    def _refresh_enclosure_capacity(self, enc_id):
        if enc_id is None:
            return
        enc = self._enc_repo.get(enc_id)
        if enc is None:
            return
        enc.current_capacity = self._repo.count_by_enclosure(enc_id)
        self._enc_repo.update(enc)
