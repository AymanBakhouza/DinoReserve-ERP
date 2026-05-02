# services/inventory_service.py
# Servicio de lógica de negocio para inventario.

from typing import List

from models.inventory import InventoryItem
from repositories.inventory_repository import InventoryRepository
from utils.exceptions import InsufficientStockError, ValidationError
from utils.logger import get_logger
from utils.validators import (
    require_int_in_range,
    require_non_empty,
    require_positive_number,
)


class InventoryService:
    def __init__(self):
        self._repo = InventoryRepository()
        self._log = get_logger()

    def list_all(self) -> List[InventoryItem]:
        return self._repo.list_all()

    def list_low_stock(self) -> List[InventoryItem]:
        return self._repo.list_low_stock()

    def _validate(self, data: dict) -> dict:
        return {
            "item_name": require_non_empty(data.get("item_name"), "nombre del ítem"),
            "category": require_non_empty(data.get("category"), "categoría"),
            "quantity": require_int_in_range(
                data.get("quantity", 0), "cantidad", 0, 1_000_000
            ),
            "minimum_stock": require_int_in_range(
                data.get("minimum_stock", 0), "stock mínimo", 0, 1_000_000
            ),
            "supplier": (data.get("supplier") or "").strip() or None,
            "price": require_positive_number(
                data.get("price", 0), "precio", allow_zero=True
            ),
        }

    def create(self, data: dict) -> int:
        clean = self._validate(data)
        new_id = self._repo.create(InventoryItem(**clean))
        self._log.info("Inventario creado id=%s '%s'", new_id, clean["item_name"])
        if InventoryItem(**clean).is_low_stock():
            self._log.warning(
                "Stock bajo desde la creación: '%s' (%d < %d)",
                clean["item_name"], clean["quantity"], clean["minimum_stock"],
            )
        return new_id

    def update(self, item_id: int, data: dict) -> None:
        clean = self._validate(data)
        if self._repo.get(item_id) is None:
            raise ValidationError("Ítem no encontrado.")
        self._repo.update(InventoryItem(id=item_id, **clean))
        self._log.info("Inventario actualizado id=%s", item_id)

    def delete(self, item_id: int) -> None:
        self._repo.delete(item_id)
        self._log.info("Inventario eliminado id=%s", item_id)

    def add_stock(self, item_id: int, qty: int) -> InventoryItem:
        item = self._repo.get(item_id)
        if item is None:
            raise ValidationError("Ítem no encontrado.")
        if qty <= 0:
            raise ValidationError("La cantidad a añadir debe ser positiva.")
        new_qty = item.quantity + qty
        self._repo.update_quantity(item_id, new_qty)
        self._log.info("Stock +%d en '%s' (total=%d)", qty, item.item_name, new_qty)
        return self._repo.get(item_id)

    def reduce_stock(self, item_id: int, qty: int) -> InventoryItem:
        item = self._repo.get(item_id)
        if item is None:
            raise ValidationError("Ítem no encontrado.")
        if qty <= 0:
            raise ValidationError("La cantidad a reducir debe ser positiva.")
        if item.quantity - qty < 0:
            raise InsufficientStockError(
                f"Stock insuficiente para '{item.item_name}' ({item.quantity})."
            )
        new_qty = item.quantity - qty
        self._repo.update_quantity(item_id, new_qty)
        self._log.info("Stock -%d en '%s' (total=%d)", qty, item.item_name, new_qty)
        if new_qty < item.minimum_stock:
            self._log.warning(
                "STOCK BAJO: '%s' quedan %d (mínimo %d)",
                item.item_name, new_qty, item.minimum_stock,
            )
        return self._repo.get(item_id)
