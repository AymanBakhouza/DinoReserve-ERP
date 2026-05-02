"""Hero banners."""
import tkinter as tk
from tkinter import ttk


class HeroBanner(ttk.Frame):
    def __init__(self, master, title: str, subtitle: str):
        super().__init__(master, style="Card.TFrame", padding=(18, 16))
        ttk.Label(self, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(4, 0))
        line = tk.Frame(self, bg="#ffb300", height=2)
        line.pack(fill="x", pady=(10, 0))
