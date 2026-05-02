#------------------------------------------------------------------------------
# descripcion del proyecto: DinoReserve ERP - Sistema de gestión para un parque temático de dinosaurios.
# Este proyecto es una aplicación de escritorio desarrollada en Python utilizando Tkinter para la interfaz gráfica y SQLite para la gestión de datos. El sistema permite administrar recintos, especies, individuos, ventas
#de tickets, y generar reportes, todo con un enfoque en la robustez, usabilidad y mantenibilidad.
# autor: AYMAN BAKHOUZA
# fecha de creación: 2024-04-29
#------------------------------------------------------------------------------

import sys
import tkinter as tk
from tkinter import messagebox

from database.init_db import initialize_database
from utils.constants import APP_NAME
from utils.logger import get_logger
from views.dashboard_view import DashboardView
from views.login_view import LoginView


def main() -> int:
    log = get_logger()
    log.info("=" * 60)
    log.info("Iniciando %s", APP_NAME)
    try:
        initialize_database()
    except Exception as exc:  # init de DB es crítico
        log.error("Fallo crítico inicializando la base de datos: %s", exc)
        # mostrar ventana de error si Tk está disponible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error crítico",
                f"No se pudo inicializar la base de datos:\n\n{exc}",
            )
            root.destroy()
        except Exception:
            print(f"Error crítico: {exc}")
        return 1

    # Bucle login → dashboard → login (logout) → …
    while True:
        login = LoginView()
        login.mainloop()
        if not login._user:  # cerró la ventana sin loguearse
            log.info("Aplicación cerrada desde login.")
            return 0
        user = login._user
        log.info("Abriendo dashboard para %s", user["username"])
        dash = DashboardView(user)
        dash.mainloop()
        if not getattr(dash, "logged_out", False):
            log.info("Aplicación cerrada desde dashboard.")
            return 0
        # Sólo el logout explícito vuelve al login.
        log.info("Sesión cerrada. Volviendo al login.")


if __name__ == "__main__":
    sys.exit(main())
