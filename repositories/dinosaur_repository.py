# repositories/dinosaur_repository.py

from typing import List, Optional

from models.dinosaur import Dinosaur
from repositories.base_repository import BaseRepository


class DinosaurRepository(BaseRepository):
    def list_all(self) -> List[Dinosaur]:
        rows = self._fetch_all(
            "SELECT * FROM dinosaurs ORDER BY id ASC"
        )
        return [Dinosaur.from_row(r) for r in rows]

    def get(self, dino_id: int) -> Optional[Dinosaur]:
        row = self._fetch_one("SELECT * FROM dinosaurs WHERE id = ?", (dino_id,))
        return Dinosaur.from_row(row) if row else None

    def create(self, dino: Dinosaur) -> int:
        return self._execute(
            """INSERT INTO dinosaurs (name, species, diet_type, danger_level,
                                       health_status, enclosure_id, feeding_level)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                dino.name, dino.species, dino.diet_type, dino.danger_level,
                dino.health_status, dino.enclosure_id, dino.feeding_level,
            ),
        )

    def update(self, dino: Dinosaur) -> None:
        self._execute(
            """UPDATE dinosaurs
                  SET name=?, species=?, diet_type=?, danger_level=?,
                      health_status=?, enclosure_id=?, feeding_level=?
                WHERE id=?""",
            (
                dino.name, dino.species, dino.diet_type, dino.danger_level,
                dino.health_status, dino.enclosure_id, dino.feeding_level,
                dino.id,
            ),
        )

    def delete(self, dino_id: int) -> None:
        self._execute("DELETE FROM dinosaurs WHERE id = ?", (dino_id,))

    def count_by_enclosure(self, enclosure_id: int) -> int:
        row = self._fetch_one(
            "SELECT COUNT(*) AS c FROM dinosaurs WHERE enclosure_id = ?",
            (enclosure_id,),
        )
        return row["c"] if row else 0

    def update_feeding(self, dino_id: int, new_level: int) -> None:
        self._execute(
            "UPDATE dinosaurs SET feeding_level = ? WHERE id = ?",
            (max(0, min(100, new_level)), dino_id),
        )

    def update_health(self, dino_id: int, status: str) -> None:
        self._execute(
            "UPDATE dinosaurs SET health_status = ? WHERE id = ?",
            (status, dino_id),
        )
