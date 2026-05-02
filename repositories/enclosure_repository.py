# repositories/enclosure_repository.py
from typing import List, Optional

from models.enclosure import Enclosure
from repositories.base_repository import BaseRepository


class EnclosureRepository(BaseRepository):
    def list_all(self) -> List[Enclosure]:
        rows = self._fetch_all("SELECT * FROM enclosures ORDER BY id ASC")
        return [Enclosure.from_row(r) for r in rows]

    def get(self, enc_id: int) -> Optional[Enclosure]:
        row = self._fetch_one("SELECT * FROM enclosures WHERE id = ?", (enc_id,))
        return Enclosure.from_row(row) if row else None

    def create(self, enc: Enclosure) -> int:
        return self._execute(
            """INSERT INTO enclosures (name, zone_type, max_capacity, current_capacity,
                                        fence_voltage, security_level, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                enc.name, enc.zone_type, enc.max_capacity, enc.current_capacity,
                enc.fence_voltage, enc.security_level, enc.status,
            ),
        )

    def update(self, enc: Enclosure) -> None:
        self._execute(
            """UPDATE enclosures
                  SET name=?, zone_type=?, max_capacity=?, current_capacity=?,
                      fence_voltage=?, security_level=?, status=?
                WHERE id=?""",
            (
                enc.name, enc.zone_type, enc.max_capacity, enc.current_capacity,
                enc.fence_voltage, enc.security_level, enc.status, enc.id,
            ),
        )

    def delete(self, enc_id: int) -> None:
        self._execute("DELETE FROM enclosures WHERE id = ?", (enc_id,))

    def update_voltage(self, enc_id: int, voltage: float) -> None:
        self._execute(
            "UPDATE enclosures SET fence_voltage = ? WHERE id = ?",
            (voltage, enc_id),
        )

    def update_status(self, enc_id: int, status: str) -> None:
        self._execute(
            "UPDATE enclosures SET status = ? WHERE id = ?", (status, enc_id)
        )
