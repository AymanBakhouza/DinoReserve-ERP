# services/auth_service.py
# Servicio de autenticación y gestión de usuarios.


import hashlib

from repositories.base_repository import BaseRepository
from utils.exceptions import AuthenticationError, ValidationError
from utils.logger import get_logger
from utils.validators import require_non_empty


class AuthService(BaseRepository):
    USER_ROLES = {"admin", "administrador", "operador", "operator"}

    def __init__(self):
        super().__init__()
        self._log = get_logger()

    @staticmethod
    def hash_password(plain: str) -> str:
        return hashlib.sha256(plain.encode("utf-8")).hexdigest()

    def login(self, username: str, password: str) -> dict:
        # Valida campos y busca el usuario en la base de datos. Si no coincide, lanza AuthenticationError.
        try:
            username = require_non_empty(username, "usuario")
            password = require_non_empty(password, "contraseña")
        except ValidationError as exc:
            self._log.warning("Login fallido (campos vacíos): %s", exc.message)
            raise AuthenticationError(exc.message) from exc

        row = self._fetch_one(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )

        if row is None or row["password_hash"] != self.hash_password(password):
            self._log.warning("Login fallido para usuario '%s'", username)
            raise AuthenticationError("Usuario o contraseña incorrectos.")

        self._log.info("Login OK: %s (%s)", row["username"], row["role"])
        return {"id": row["id"], "username": row["username"], "role": row["role"]}

    def register_user(self, username: str, password: str, confirm_password: str, role: str = "operador") -> dict:
        """Crea una cuenta nueva y devuelve los datos básicos del usuario."""
        username = require_non_empty(username, "usuario").strip()
        password = require_non_empty(password, "contraseña")
        confirm_password = require_non_empty(confirm_password, "confirmación de contraseña")
        role = (role or "operador").strip().lower()

        if len(username) < 3:
            raise ValidationError("El usuario debe tener al menos 3 caracteres.")
        if len(password) < 6:
            raise ValidationError("La contraseña debe tener al menos 6 caracteres.")
        if password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        if role not in self.USER_ROLES:
            raise ValidationError("El rol seleccionado no es válido.")
        if role in {"administrador"}:
            role = "admin"
        if role in {"operator"}:
            role = "operador"

        existing = self._fetch_one(
            "SELECT id FROM users WHERE lower(username) = lower(?)",
            (username,),
        )
        if existing is not None:
            raise ValidationError("Ya existe una cuenta con ese usuario.")

        user_id = self._execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, self.hash_password(password), role),
        )
        self._log.info("Cuenta creada: %s (%s)", username, role)
        return {"id": user_id, "username": username, "role": role}
