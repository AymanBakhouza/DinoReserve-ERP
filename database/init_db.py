"""Inicializador de la base de datos: crea el archivo SQLite si no existe
y ejecuta el script schema.sql con datos de demostración."""
import sqlite3

from utils.constants import DB_PATH, LEGACY_DB_PATH, SCHEMA_PATH
from utils.exceptions import DatabaseOperationError
from utils.logger import get_logger

logger = get_logger()

def _migrate_legacy_db_if_needed() -> None:
    """Si existe dinoreserve.db, lo renombra a 'DinoReserve ERP DATABASE.db'."""
    try:
        if DB_PATH.exists():
            return
        if LEGACY_DB_PATH.exists():
            LEGACY_DB_PATH.replace(DB_PATH)
            logger.info("Base de datos migrada: %s -> %s", LEGACY_DB_PATH, DB_PATH)
    except Exception as exc:
        logger.warning("No se pudo migrar base de datos legacy: %s", exc)


def database_exists() -> bool:
    """¿Ya hay un archivo .db con tablas?"""
    _migrate_legacy_db_if_needed()
    if not DB_PATH.exists():
        return False
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users'"
        )
        ok = cur.fetchone()[0] > 0
        conn.close()
        return ok
    except sqlite3.Error:
        return False


def initialize_database(force: bool = False) -> None:
    """Ejecuta schema.sql si la base de datos no existe (o si force=True)."""
    _migrate_legacy_db_if_needed()
    if database_exists() and not force:
        logger.info("Base de datos existente: %s", DB_PATH)
        return

    if not SCHEMA_PATH.exists():
        raise DatabaseOperationError(f"No se encontró el schema: {SCHEMA_PATH}")

    logger.info("Creando base de datos en %s desde %s", DB_PATH, SCHEMA_PATH)
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.executescript(sql)
        conn.commit()
        conn.close()
    except sqlite3.Error as exc:
        logger.error("Fallo creando la base de datos: %s", exc)
        raise DatabaseOperationError(str(exc)) from exc

    logger.info("Base de datos inicializada correctamente con datos demo.")


if __name__ == "__main__":  # ejecución directa
    initialize_database(force=False)
    print(f"Base de datos lista en: {DB_PATH}")
