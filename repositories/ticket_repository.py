# repositories/ticket_repository.py
from typing import List, Optional

from models.ticket import Ticket
from repositories.base_repository import BaseRepository


class TicketRepository(BaseRepository):
    def list_all(self) -> List[Ticket]:
        rows = self._fetch_all(
            "SELECT * FROM tickets ORDER BY sale_date DESC, id DESC"
        )
        return [Ticket.from_row(r) for r in rows]

    def get(self, ticket_id: int) -> Optional[Ticket]:
        row = self._fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        return Ticket.from_row(row) if row else None

    def get_by_locator(self, locator: str) -> Optional[Ticket]:
        row = self._fetch_one(
            "SELECT * FROM tickets WHERE locator_code = ?", (locator,)
        )
        return Ticket.from_row(row) if row else None

    def create_in_transaction(self, ticket: Ticket) -> int:
        """Inserta un ticket dentro de una transacción explícita."""
        with self._db.transaction() as cur:
            cur.execute(
                """INSERT INTO tickets (visitor_name, ticket_type, price, iva,
                                        total, locator_code)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    ticket.visitor_name, ticket.ticket_type, ticket.price,
                    ticket.iva, ticket.total, ticket.locator_code,
                ),
            )
            return cur.lastrowid

    def delete(self, ticket_id: int) -> None:
        self._execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
