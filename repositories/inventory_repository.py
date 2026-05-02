# repositories/inventory_repository.py
from typing import List, Optional

from models.inventory import InventoryItem
from repositories.base_repository import BaseRepository


class InventoryRepository(BaseRepository):
    def list_all(self) -> List[InventoryItem]:
        rows = self._fetch_all("SELECT * FROM inventory ORDER BY id ASC")
        return [InventoryItem.from_row(r) for r in rows]

    def list_low_stock(self) -> List[InventoryItem]:
        rows = self._fetch_all(
            "SELECT * FROM inventory WHERE quantity < minimum_stock ORDER BY id ASC"
        )
        return [InventoryItem.from_row(r) for r in rows]

    def get(self, item_id: int) -> Optional[InventoryItem]:
        row = self._fetch_one("SELECT * FROM inventory WHERE id = ?", (item_id,))
        return InventoryItem.from_row(row) if row else None

    def create(self, item: InventoryItem) -> int:
        return self._execute(
            """INSERT INTO inventory (item_name, category, quantity,
                                       minimum_stock, supplier, price)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (item.item_name, item.category, item.quantity,
             item.minimum_stock, item.supplier, item.price),
        )

    def update(self, item: InventoryItem) -> None:
        self._execute(
            """UPDATE inventory
                  SET item_name=?, category=?, quantity=?, minimum_stock=?,
                      supplier=?, price=?
                WHERE id=?""",
            (item.item_name, item.category, item.quantity, item.minimum_stock,
             item.supplier, item.price, item.id),
        )

    def update_quantity(self, item_id: int, new_qty: int) -> None:
        self._execute(
            "UPDATE inventory SET quantity = ? WHERE id = ?",
            (max(0, new_qty), item_id),
        )

    def delete(self, item_id: int) -> None:
        self._execute("DELETE FROM inventory WHERE id = ?", (item_id,))
