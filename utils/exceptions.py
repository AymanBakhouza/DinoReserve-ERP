# utils/exceptions.py
# Excepciones personalizadas para el dominio de DinoReserve.
# Todas las excepciones específicas del dominio heredan de DinoReserveError para facilitar su manejo centralizado.

class DinoReserveError(Exception):
    # Excepción base para errores específicos de DinoReserve.

    def __init__(self, message: str = "Error en DinoReserve"):
        super().__init__(message)
        self.message = message


class CapacityExceededError(DinoReserveError):
    """Se lanza cuando un recinto recibe más individuos que su capacidad máxima."""


class InsufficientStockError(DinoReserveError):
    """Se lanza cuando se intenta reducir stock por debajo de cero."""


class DatabaseOperationError(DinoReserveError):
    """Error genérico envolviendo problemas de SQLite."""


class InvalidTicketError(DinoReserveError):
    """Datos de venta de ticket inválidos (precio, tipo, visitante…)."""


class FenceSecurityError(DinoReserveError):
    """Problema de voltaje o nivel de seguridad de una valla."""


class ValidationError(DinoReserveError):
    """Validación de formulario (uso interno en utils.validators)."""


class AuthenticationError(DinoReserveError):
    """Credenciales inválidas durante el login."""
