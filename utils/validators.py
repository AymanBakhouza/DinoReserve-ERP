# utils/validators.py
# Validadores de datos y formularios para DinoReserve ERP.
# Incluye validadores de tipo, rango, opciones y validadores específicos para Tkinter.

import re

from utils.exceptions import ValidationError


def require_non_empty(value: str, field: str) -> str:
    """Asegura que un campo de texto no esté vacío."""
    if value is None or str(value).strip() == "":
        raise ValidationError(f"El campo '{field}' es obligatorio.")
    return str(value).strip()


def require_positive_number(value, field: str, allow_zero: bool = False) -> float:
    """Convierte a float y exige que sea positivo."""
    try:
        v = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"El campo '{field}' debe ser numérico.") from exc
    if allow_zero and v < 0:
        raise ValidationError(f"El campo '{field}' no puede ser negativo.")
    if not allow_zero and v <= 0:
        raise ValidationError(f"El campo '{field}' debe ser mayor que cero.")
    return v


def require_int_in_range(value, field: str, lo: int, hi: int) -> int:
    """Convierte a int y exige que esté en [lo, hi]."""
    try:
        v = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"El campo '{field}' debe ser entero.") from exc
    if v < lo or v > hi:
        raise ValidationError(f"El campo '{field}' debe estar entre {lo} y {hi}.")
    return v


def require_in_options(value: str, field: str, options) -> str:
    """Asegura que el valor pertenezca a un conjunto de opciones."""
    if value not in options:
        raise ValidationError(
            f"El campo '{field}' debe ser uno de: {', '.join(options)}."
        )
    return value


# Validadores de Tkinter (devuelven True/False; útiles en register=...)
def tk_validate_int(proposed: str) -> bool:
    """Permite vacío o sólo dígitos (entero positivo)."""
    return proposed == "" or proposed.isdigit()


def tk_validate_float(proposed: str) -> bool:
    """Permite vacío, dígitos y un punto decimal."""
    if proposed == "":
        return True
    return bool(re.fullmatch(r"\d*\.?\d*", proposed))
