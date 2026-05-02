# repositories/base_repository.py
from typing import Iterable, List

from database.connection import DatabaseConnection


class BaseRepository:
# Repositorio base con métodos comunes para acceso a datos.
    def __init__(self):
        self._db = DatabaseConnection()

    # Helpers para ejecutar consultas SQL y mapear resultados a objetos.
    def _fetch_all(self, sql: str, params: Iterable = ()) -> List:
        with self._db.cursor() as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()

    def _fetch_one(self, sql: str, params: Iterable = ()):
        with self._db.cursor() as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchone()

    def _execute(self, sql: str, params: Iterable = ()) -> int:
        with self._db.cursor() as cur:
            cur.execute(sql, tuple(params))
            return cur.lastrowid or cur.rowcount
