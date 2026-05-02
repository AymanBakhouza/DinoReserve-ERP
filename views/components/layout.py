"""Layout base para módulos."""
from tkinter import ttk


class BaseModuleView(ttk.Frame):
    """Base para páginas de módulos."""

    def __init__(self, master):
        super().__init__(master)


class SidebarNavButton(ttk.Button):
    """Botón de navegación lateral con estilo consistente."""

    def set_active(self, active: bool) -> None:
        self.configure(style="NavActive.TButton" if active else "Nav.TButton")
