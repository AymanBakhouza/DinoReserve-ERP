"""Tarjetas reutilizables."""
import tkinter as tk
from tkinter import ttk


class FuturisticCard(ttk.Frame):
    def __init__(self, master, title: str = "", padding=(14, 12), **kwargs):
        super().__init__(master, style="Card.TFrame", padding=padding, **kwargs)
        if title:
            ttk.Label(self, text=title, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))


class KpiCard(ttk.Frame):
    def __init__(self, master, title: str, value: str, accent: str = "#ffb300"):
        super().__init__(master, style="Card.TFrame")
        tk.Frame(self, bg=accent, height=3).pack(fill="x")
        inner = ttk.Frame(self, style="Card.TFrame", padding=(12, 10))
        inner.pack(fill="both", expand=True)
        ttk.Label(inner, text=title, style="Muted.TLabel").pack(anchor="w")
        ttk.Label(inner, text=value, style="CardValue.TLabel").pack(anchor="w", pady=(2, 0))
