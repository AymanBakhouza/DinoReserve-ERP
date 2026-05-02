"""Tema central de la interfaz Neo-Jurassic."""
from utils.constants import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BG_ALT,
    COLOR_BG_CARD,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_WARNING,
)

PALETTE = {
    "bg": COLOR_BG,
    "bg_alt": COLOR_BG_ALT,
    "card": COLOR_BG_CARD,
    "border": COLOR_BORDER,
    "text": COLOR_TEXT,
    "muted": COLOR_TEXT_MUTED,
    "accent": COLOR_ACCENT,
    "primary": COLOR_PRIMARY,
    "success": COLOR_SUCCESS,
    "danger": COLOR_DANGER,
    "warning": COLOR_WARNING,
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 18,
    "xl": 24,
    "xxl": 32,
}

MODULE_SYSTEMS = {
    "default": {"accent": "#D9A441", "neon": "#4DE6A2", "chip": "NÚCLEO"},
    "dinosaurs": {"accent": "#35E879", "neon": "#8CFFB0", "chip": "FAUNA"},
    "security": {"accent": "#FF5D5D", "neon": "#FF9C85", "chip": "SEGURIDAD"},
    "logistics": {"accent": "#D9A441", "neon": "#F2C66D", "chip": "LOGÍSTICA"},
    "maintenance": {"accent": "#C85C4B", "neon": "#FF9C85", "chip": "TALLER"},
    "analytics": {"accent": "#7FE7A8", "neon": "#C6F6D5", "chip": "ANALÍTICA"},
    "sales": {"accent": "#D9A441", "neon": "#F4D27C", "chip": "ENTRADAS"},
    "hr": {"accent": "#9BD26D", "neon": "#D4F58D", "chip": "PERSONAL"},
}

MODULE_ICONS = {
    "default": "◉",
    "dinosaurs": "🦖",
    "security": "🛡",
    "logistics": "📦",
    "maintenance": "🛠",
    "analytics": "📈",
    "sales": "🎟",
    "hr": "👥",
}


def module_system(module_key: str) -> dict[str, str]:
    return MODULE_SYSTEMS.get(module_key, MODULE_SYSTEMS["default"])


def module_icon(module_key: str) -> str:
    return MODULE_ICONS.get(module_key, MODULE_ICONS["default"])
