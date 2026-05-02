# services/ticket_service.py
# Servicio de lógica de negocio para la venta y gestión de tickets.

import secrets
import string
from typing import List

from models.ticket import Ticket
from repositories.ticket_repository import TicketRepository
from utils.constants import IVA_RATE, TICKET_TYPES
from utils.exceptions import InvalidTicketError
from utils.logger import get_logger
from utils.validators import require_non_empty


class TicketService:
    def __init__(self):
        self._repo = TicketRepository()
        self._log = get_logger()

    def list_all(self) -> List[Ticket]:
        return self._repo.list_all()

    @staticmethod
    def generate_locator() -> str:
        """Genera un código de localizador único alfanumérico."""
        alphabet = string.ascii_uppercase + string.digits
        return "DR-" + "".join(secrets.choice(alphabet) for _ in range(8))

    def _unique_locator(self) -> str:
        for _ in range(8):
            code = self.generate_locator()
            if self._repo.get_by_locator(code) is None:
                return code
        raise InvalidTicketError("No se pudo generar un localizador único.")

    def sell_ticket(self, visitor_name: str, ticket_type: str) -> Ticket:
        """Vende un ticket dentro de una transacción SQLite."""
        try:
            visitor_name = require_non_empty(visitor_name, "nombre del visitante")
        except Exception as exc:
            raise InvalidTicketError(str(exc)) from exc

        if ticket_type not in TICKET_TYPES:
            raise InvalidTicketError(
                f"Tipo de ticket inválido: '{ticket_type}'."
            )

        price = TICKET_TYPES[ticket_type]
        iva = round(price * IVA_RATE, 2)
        total = round(price + iva, 2)
        locator = self._unique_locator()

        ticket = Ticket(
            visitor_name=visitor_name,
            ticket_type=ticket_type,
            price=price,
            iva=iva,
            total=total,
            locator_code=locator,
        )
        new_id = self._repo.create_in_transaction(ticket)
        ticket.id = new_id
        self._log.info(
            "VENTA TICKET — id=%s tipo=%s visitante='%s' total=%.2f loc=%s",
            new_id, ticket_type, visitor_name, total, locator,
        )
        return self._repo.get(new_id)

    def delete(self, ticket_id: int) -> None:
        self._repo.delete(ticket_id)
        self._log.info("Ticket eliminado id=%s", ticket_id)
