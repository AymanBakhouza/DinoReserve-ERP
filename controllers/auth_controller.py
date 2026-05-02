# controllers/auth_controller.py
from services.auth_service import AuthService
from utils.exceptions import AuthenticationError


class AuthController:
    def __init__(self):
        self._service = AuthService()

    def login(self, username: str, password: str) -> dict:
        """Devuelve el dict de usuario o relanza AuthenticationError."""
        try:
            return self._service.login(username, password)
        except AuthenticationError:
            raise

    def register(self, username: str, password: str, confirm_password: str, role: str) -> dict:
        """Crea una cuenta nueva para acceder al sistema."""
        return self._service.register_user(username, password, confirm_password, role)
