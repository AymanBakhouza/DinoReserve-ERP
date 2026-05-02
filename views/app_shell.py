"""Shell principal reutilizable para pantallas con barra superior."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class AppShell(ttk.Frame):
    """Contenedor con topbar y body para páginas avanzadas."""

    def __init__(self, master, title: str, subtitle: str):
        super().__init__(master)
        top = ttk.Frame(self, style="Card.TFrame", padding=(18, 12))
        top.pack(fill="x")
        ttk.Label(top, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(top, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(2, 0))
        tk.Frame(top, bg="#ffb300", height=2).pack(fill="x", pady=(8, 0))
        self.body = ttk.Frame(self)
        self.body.pack(fill="both", expand=True)
