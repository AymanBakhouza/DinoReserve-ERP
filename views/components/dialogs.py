"""Diálogos comunes."""
from tkinter import messagebox


def confirm_dialog(parent, title: str, text: str) -> bool:
    return bool(messagebox.askyesno(title, text, parent=parent))
