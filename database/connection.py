"""Gestor de conexiones SQLite. Patrón Singleton ligero por proceso."""
import sqlite3
from contextlib import contextmanager

from utils.constants import DB_PATH
from utils.exceptions import DatabaseOperationError
from utils.logger import get_logger

logger = get_logger()


class DatabaseConnection:
    """Encapsula la conexión a SQLite con foreign keys habilitadas."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._db_path = str(DB_PATH)
        self._initialized = True

    def _connect(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self._db_path, timeout=10, isolation_level=None)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as exc:
            logger.error("No se pudo abrir SQLite (%s): %s", self._db_path, exc)
            raise DatabaseOperationError(f"No se pudo abrir la base de datos: {exc}") from exc

    @contextmanager
    def cursor(self):
        """Context manager para una conexión + cursor de uso puntual."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            yield cur
        except sqlite3.Error as exc:
            logger.error("Error SQLite: %s", exc)
            raise DatabaseOperationError(str(exc)) from exc
        finally:
            conn.close()

    @contextmanager
    def transaction(self):
        """Context manager con BEGIN/COMMIT/ROLLBACK explícitos."""
        conn = self._connect()
        try:
            conn.execute("BEGIN")
            cur = conn.cursor()
            yield cur
            conn.execute("COMMIT")
        except sqlite3.Error as exc:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            logger.error("Transacción revertida por error: %s", exc)
            raise DatabaseOperationError(str(exc)) from exc
        finally:
            conn.close()
