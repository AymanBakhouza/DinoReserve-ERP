"""Badges de estado."""
from tkinter import ttk


class StatusBadge(ttk.Label):
    def __init__(self, master, text: str):
        super().__init__(master, text=f"  {text}  ", style="Chip.TLabel")
