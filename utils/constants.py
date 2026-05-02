# utils/constants.py
# Constantes globales para rutas, configuración visual y reglas de negocio.

from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "DinoReserve ERP DATABASE.db"
LEGACY_DB_PATH = BASE_DIR / "dinoreserve.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
LOG_PATH = BASE_DIR / "log_parque.txt"
ASSETS_DIR = BASE_DIR / "assets"
DEFAULT_LOGO_PATH = ASSETS_DIR / "logo.png"

# Ruta fallback al logo compartido por Cursor (si el usuario aun no copio el archivo)
CURSOR_LOGO_FALLBACK = Path(
    r"C:\Users\astam\.cursor\projects\c-Users-astam-Downloads-dinoreserve\assets"
    r"\c__Users_astam_AppData_Roaming_Cursor_User_workspaceStorage_"
    r"9d896ffbf66b58cbabb158d79e41f96a_images_image-5f610623-4646-40f0-9aee-d56ecdae4451.png"
)

# Aplicación
APP_NAME = "DinoReserve"
APP_VERSION = "2.0.0"
APP_AUTHOR = "DinoReserve Team"

# Tema visual DinoReserve (jungla futurista / fósil neón)
COLOR_BG = "#06110B"
COLOR_BG_ALT = "#0B1C12"
COLOR_BG_CARD = "#102719"
COLOR_PRIMARY = "#35E879"
COLOR_PRIMARY_HOVER = "#74FF9E"
COLOR_ACCENT = "#D9A441"
COLOR_ACCENT_HOVER = "#F2C66D"
COLOR_DANGER = "#FF5D5D"
COLOR_WARNING = "#FFB84D"
COLOR_SUCCESS = "#4DE6A2"
COLOR_TEXT = "#F1FFF5"
COLOR_TEXT_MUTED = "#9EC7AA"
COLOR_BORDER = "#2F6543"

FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 23, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
FONT_NORMAL = (FONT_FAMILY, 10)
FONT_SMALL = (FONT_FAMILY, 9)
FONT_BUTTON = (FONT_FAMILY, 10, "bold")

# Reglas de negocio
IVA_RATE = 0.21  # 21%

TICKET_TYPES = {
    "normal": 25.00,
    "child": 15.00,
    "vip": 60.00,
    "fast_pass": 45.00,
}

DIET_TYPES = ("carnivore", "herbivore", "omnivore")
HEALTH_STATUSES = ("healthy", "observation", "sick", "critical")
ENCLOSURE_STATUSES = ("active", "maintenance", "closed")
MAINTENANCE_STATUSES = ("pending", "in_progress", "completed", "cancelled")
MAINTENANCE_PRIORITIES = ("low", "medium", "high", "critical")
EMPLOYEE_ROLES = (
    "Veterinario", "Guardia de seguridad", "Técnico",
    "Vendedor de tickets", "Limpiador", "Gerente",
)
EMPLOYEE_STATUSES = ("active", "inactive", "vacation")

# Eventos aleatorios — probabilidades (deben sumar 1.0)
RANDOM_EVENTS = [
    ("tropical_storm", 0.18),
    ("feeding_delay", 0.22),
    ("stock_variation", 0.22),
    ("fence_malfunction", 0.15),
    ("dinosaur_health_alert", 0.18),
    ("calm_day", 0.05),
]
