# models/inventory.py
from dataclasses import dataclass
from typing import Optional

from models.base import Entity


@dataclass
class InventoryItem(Entity):
    item_name: str = ""
    category: str = ""
    quantity: int = 0
    minimum_stock: int = 0
    supplier: Optional[str] = None
    price: float = 0.0

    def is_low_stock(self) -> bool:
        return self.quantity < self.minimum_stock

    def display_name(self) -> str:
        return f"{self.item_name} ({self.category})"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "item_name": self.item_name,
            "category": self.category,
            "quantity": self.quantity,
            "minimum_stock": self.minimum_stock,
            "supplier": self.supplier,
            "price": self.price,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row) -> "InventoryItem":
        return cls(
            id=row["id"],
            item_name=row["item_name"],
            category=row["category"],
            quantity=row["quantity"],
            minimum_stock=row["minimum_stock"],
            supplier=row["supplier"],
            price=row["price"],
            created_at=row["created_at"],
        )
