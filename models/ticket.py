# models/ticket.py
from dataclasses import dataclass

from models.base import Entity


@dataclass
class Ticket(Entity):
    visitor_name: str = ""
    ticket_type: str = "normal"
    price: float = 0.0
    iva: float = 0.0
    total: float = 0.0
    locator_code: str = ""
    sale_date: str = ""

    def display_name(self) -> str:
        return f"{self.locator_code} — {self.visitor_name} ({self.ticket_type})"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "visitor_name": self.visitor_name,
            "ticket_type": self.ticket_type,
            "price": self.price,
            "iva": self.iva,
            "total": self.total,
            "locator_code": self.locator_code,
            "sale_date": self.sale_date,
        }

    @classmethod
    def from_row(cls, row) -> "Ticket":
        return cls(
            id=row["id"],
            visitor_name=row["visitor_name"],
            ticket_type=row["ticket_type"],
            price=row["price"],
            iva=row["iva"],
            total=row["total"],
            locator_code=row["locator_code"],
            sale_date=row["sale_date"],
            created_at=row["sale_date"],
        )
