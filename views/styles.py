"""Configuración global de estilos ttk para todas las vistas."""
import tkinter as tk
from tkinter import ttk

from utils.constants import (
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_BG,
    COLOR_BG_ALT,
    COLOR_BG_CARD,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SUCCESS,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    FONT_BUTTON,
    FONT_NORMAL,
    FONT_SUBTITLE,
    FONT_TITLE,
)


def configure_styles(root: tk.Misc) -> None:
    """Aplica el tema Neo-Jurassic HUD a la aplicación."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Fondos generales
    root.configure(bg=COLOR_BG)
    style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT, font=FONT_NORMAL)

    # Frames y Labels
    style.configure("TFrame", background=COLOR_BG)
    style.configure("Card.TFrame", background=COLOR_BG_CARD, relief="flat", borderwidth=1)
    style.configure("Pulse.Card.TFrame", background="#183C26", relief="flat", borderwidth=1)
    style.configure("Side.TFrame", background=COLOR_BG_ALT)
    style.configure("Toolbar.TFrame", background="#102719", relief="flat", borderwidth=1)
    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=FONT_NORMAL)
    style.configure("Card.TLabel", background=COLOR_BG_CARD, foreground=COLOR_TEXT,
                    font=FONT_NORMAL)
    style.configure("Title.TLabel", background=COLOR_BG, foreground=COLOR_TEXT,
                    font=("Segoe UI", 28, "bold"))
    style.configure("Subtitle.TLabel", background=COLOR_BG, foreground=COLOR_TEXT,
                    font=("Segoe UI", 13, "bold"))
    style.configure("Muted.TLabel", background=COLOR_BG, foreground=COLOR_TEXT_MUTED,
                    font=("Segoe UI", 10))
    style.configure("CardTitle.TLabel", background=COLOR_BG_CARD,
                    foreground=COLOR_TEXT, font=("Segoe UI", 13, "bold"))
    style.configure("CardValue.TLabel", background=COLOR_BG_CARD,
                    foreground=COLOR_TEXT, font=(FONT_TITLE[0], 22, "bold"))
    style.configure("HudValue.TLabel", background=COLOR_BG_CARD,
                    foreground=COLOR_ACCENT, font=(FONT_TITLE[0], 18, "bold"))
    style.configure("Chip.TLabel", background="#0E2E1B", foreground=COLOR_PRIMARY,
                    font=(FONT_NORMAL[0], 9, "bold"))

    # Entradas
    style.configure(
        "TEntry",
        fieldbackground=COLOR_BG_CARD,
        background=COLOR_BG_CARD,
        foreground=COLOR_TEXT,
        bordercolor=COLOR_BORDER,
        lightcolor=COLOR_BORDER,
        darkcolor=COLOR_BORDER,
        insertcolor=COLOR_TEXT,
    )
    style.map("TEntry", fieldbackground=[("focus", COLOR_BG_CARD)])
    style.configure(
        "TSpinbox",
        fieldbackground=COLOR_BG_CARD,
        background=COLOR_BG_CARD,
        foreground=COLOR_TEXT,
        bordercolor=COLOR_BORDER,
        lightcolor=COLOR_BORDER,
        darkcolor=COLOR_BORDER,
        insertcolor=COLOR_TEXT,
        arrowcolor=COLOR_ACCENT,
    )
    style.map("TSpinbox", fieldbackground=[("focus", COLOR_BG_CARD)])
    style.configure(
        "TCombobox",
        fieldbackground=COLOR_BG_CARD,
        background=COLOR_BG_CARD,
        foreground=COLOR_TEXT,
        arrowcolor=COLOR_ACCENT,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", COLOR_BG_CARD)],
        foreground=[("readonly", COLOR_TEXT)],
        selectbackground=[("readonly", COLOR_BG_CARD)],
        selectforeground=[("readonly", COLOR_TEXT)],
    )
    root.option_add("*TCombobox*Listbox.background", COLOR_BG_CARD)
    root.option_add("*TCombobox*Listbox.foreground", COLOR_TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", COLOR_PRIMARY)
    root.option_add("*TCombobox*Listbox.selectForeground", COLOR_TEXT)

    # Botones
    style.configure(
        "TButton",
        background=COLOR_PRIMARY,
        foreground=COLOR_TEXT,
        bordercolor=COLOR_PRIMARY,
        focusthickness=0,
        font=FONT_BUTTON,
        padding=(12, 9),
    )
    style.map(
        "TButton",
        background=[("active", COLOR_PRIMARY_HOVER), ("pressed", COLOR_PRIMARY_HOVER)],
        foreground=[("disabled", COLOR_TEXT_MUTED)],
    )
    style.configure(
        "Accent.TButton",
        background=COLOR_ACCENT,
        foreground="#06110B",
        bordercolor=COLOR_ACCENT,
        font=FONT_BUTTON,
        padding=(12, 9),
    )
    style.map(
        "Accent.TButton",
        background=[("active", COLOR_ACCENT_HOVER), ("pressed", COLOR_ACCENT_HOVER)],
    )
    style.configure(
        "Danger.TButton",
        background=COLOR_DANGER,
        foreground=COLOR_TEXT,
        bordercolor=COLOR_DANGER,
        padding=(12, 9),
    )
    style.map("Danger.TButton", background=[("active", "#e53935")])
    style.configure(
        "Success.TButton",
        background=COLOR_SUCCESS,
        foreground=COLOR_TEXT,
        bordercolor=COLOR_SUCCESS,
        font=FONT_BUTTON,
        padding=(12, 9),
    )
    style.configure(
        "Ghost.TButton",
        background="#102719",
        foreground=COLOR_TEXT,
        bordercolor=COLOR_BORDER,
        font=FONT_BUTTON,
        padding=(12, 9),
    )

    style.configure(
        "TRadiobutton",
        background=COLOR_BG_CARD,
        foreground=COLOR_TEXT,
        indicatorcolor=COLOR_BG_ALT,
        indicatormargin=6,
        font=FONT_NORMAL,
        padding=(6, 4),
    )
    style.map(
        "TRadiobutton",
        background=[("active", COLOR_BG_CARD)],
        foreground=[("active", COLOR_ACCENT), ("selected", COLOR_ACCENT)],
        indicatorcolor=[("selected", COLOR_ACCENT), ("active", COLOR_PRIMARY)],
    )

    style.configure(
        "Nav.TButton",
        background="#0B1C12",
        foreground=COLOR_TEXT,
        bordercolor="#2F6543",
        anchor="w",
        padding=(18, 13),
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "Nav.TButton",
        background=[("active", "#143322")],
        foreground=[("active", COLOR_PRIMARY)],
    )
    style.configure(
        "NavActive.TButton",
        background="#1B4A2A",
        foreground=COLOR_PRIMARY,
        bordercolor=COLOR_PRIMARY,
        anchor="w",
        padding=(18, 13),
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "NavActive.TButton",
        background=[("active", "#246337")],
        foreground=[("active", COLOR_ACCENT_HOVER)],
    )

    # Treeview
    style.configure(
        "Treeview",
        background="#0B1C12",
        fieldbackground="#0B1C12",
        foreground=COLOR_TEXT,
        rowheight=30,
        bordercolor=COLOR_BORDER,
        font=FONT_NORMAL,
    )
    style.configure(
        "Glow.Treeview",
        background="#09180F",
        fieldbackground="#09180F",
        foreground=COLOR_TEXT,
        rowheight=29,
        bordercolor=COLOR_ACCENT,
        font=FONT_NORMAL,
    )
    style.configure(
        "Treeview.Heading",
        background="#163621",
        foreground=COLOR_ACCENT,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padding=10,
    )
    style.map(
        "Treeview",
        background=[("selected", "#1F5E34")],
        foreground=[("selected", COLOR_TEXT)],
    )
    style.map("Treeview.Heading", background=[("active", COLOR_BG_CARD)])

    style.configure(
        "Glow.Treeview.Heading",
        background="#0B1C12",
        foreground=COLOR_PRIMARY,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padding=12,
    )
    style.layout(
        "Treeview",
        [("Treeview.treearea", {"sticky": "nswe"})],
    )

    # Notebook (pestañas) — usado en Reportes
    style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=COLOR_BG_ALT,
        foreground=COLOR_TEXT,
        padding=(14, 7),
        font=FONT_BUTTON,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLOR_BG_CARD)],
        foreground=[("selected", COLOR_ACCENT)],
    )

    # Scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=COLOR_BG_ALT,
        troughcolor=COLOR_BG,
        bordercolor=COLOR_BG_ALT,
        arrowcolor=COLOR_TEXT,
    )
