"""Componentes reutilizables para la interfaz Neo-Jurassic HUD."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from utils.constants import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BG_ALT,
    COLOR_BG_CARD,
    COLOR_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    FONT_BUTTON,
    FONT_SMALL,
)
from utils.assets import asset_path, load_photo_image

_LOGO_CACHE: dict[tuple[int, int], tk.PhotoImage] = {}


def load_brand_logo(width: int = 108, height: int = 108) -> tk.PhotoImage | None:
    """Carga el logo principal si está disponible en assets o fallback."""
    cache_key = (width, height)
    if cache_key in _LOGO_CACHE:
        return _LOGO_CACHE[cache_key]

    image = load_photo_image(asset_path("logo.png"), width=width, height=height)
    if image is None:
        return None
    _LOGO_CACHE[cache_key] = image
    return image


def make_hud_card(parent: tk.Misc, padding: tuple[int, int] = (16, 16)) -> ttk.Frame:
    """Crea una tarjeta visual consistente para paneles HUD."""
    outer = tk.Frame(parent, bg=COLOR_BG, highlightthickness=0, bd=0)
    outer.pack_propagate(False)

    glow = tk.Frame(outer, bg=COLOR_BORDER, height=2)
    glow.pack(fill="x", side="top")
    body = ttk.Frame(outer, style="Card.TFrame", padding=padding)
    body.pack(fill="both", expand=True)
    return body


def draw_kpi_tile(parent: tk.Misc, title: str, value: str, accent: str = COLOR_ACCENT) -> ttk.Frame:
    """Tarjeta KPI neon/glass para paneles de mando."""
    card = tk.Frame(parent, bg=COLOR_BG, highlightthickness=1, highlightbackground=COLOR_BORDER)
    top = tk.Frame(card, bg=accent, height=3)
    top.pack(fill="x", side="top")
    inner = tk.Frame(card, bg=COLOR_BG_CARD, padx=16, pady=13)
    inner.pack(fill="both", expand=True)
    tk.Frame(inner, bg=accent, width=28, height=2).pack(anchor="w", pady=(0, 10))
    tk.Label(
        inner,
        text=title,
        bg=COLOR_BG_CARD,
        fg=COLOR_TEXT_MUTED,
        font=("Segoe UI", 9, "bold"),
        anchor="w",
    ).pack(anchor="w", fill="x")
    tk.Label(
        inner,
        text=value,
        bg=COLOR_BG_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 24, "bold"),
        anchor="w",
    ).pack(anchor="w", fill="x", pady=(6, 0))
    return card


def make_status_pill(parent: tk.Misc, label: str) -> ttk.Label:
    """Etiqueta tipo badge para estado del sistema."""
    return ttk.Label(parent, text=f"  {label}  ", style="Chip.TLabel")


def make_empty_state(parent: tk.Misc, title: str, detail: str) -> ttk.Frame:
    """Componente reutilizable cuando no hay datos."""
    frame = ttk.Frame(parent, style="Card.TFrame", padding=(24, 18))
    ttk.Label(frame, text=title, style="Subtitle.TLabel").pack(anchor="w")
    ttk.Label(frame, text=detail, style="Muted.TLabel", wraplength=540, justify="left").pack(
        anchor="w", pady=(8, 0)
    )
    return frame


def make_glass_toolbar(parent: tk.Misc) -> ttk.Frame:
    """Barra de acciones compacta para CRUD."""
    bar = ttk.Frame(parent, style="Toolbar.TFrame", padding=(16, 10))
    return bar


def brand_footer(parent: tk.Misc) -> ttk.Label:
    return ttk.Label(
        parent,
        text="Biocomando DinoReserve",
        foreground=COLOR_TEXT_MUTED,
        background=COLOR_BG,
        font=FONT_SMALL,
    )


def style_nav_button(btn: ttk.Button, is_active: bool) -> None:
    """Aplica estado activo/inactivo a botones de navegación lateral."""
    btn.configure(style="NavActive.TButton" if is_active else "Nav.TButton")


def make_label_value_line(parent: tk.Misc, label: str, value: str) -> ttk.Frame:
    line = ttk.Frame(parent, style="Card.TFrame")
    ttk.Label(line, text=label, style="Muted.TLabel").pack(side="left")
    ttk.Label(line, text=value, style="Card.TLabel", font=FONT_BUTTON).pack(side="right")
    return line


class ScanlineOverlay(tk.Canvas):
    """Overlay ligero con escaneo HUD animado."""

    def __init__(self, master, width=600, height=180, accent="#ffb300", **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, bd=0, **kwargs)
        self.configure(bg=COLOR_BG_CARD)
        self._line_y = 0
        self._width = width
        self._height = height
        self._accent = accent
        self._line_id = self.create_rectangle(0, 0, width, 2, fill=self._accent, outline="")
        self._draw_grid()
        self._animate()

    def _draw_grid(self):
        for x in range(0, self._width, 24):
            self.create_line(x, 0, x, self._height, fill="#1E4B31")
        for y in range(0, self._height, 24):
            self.create_line(0, y, self._width, y, fill="#173A27")
        self.create_text(10, 8, anchor="nw", fill=COLOR_ACCENT, font=("Consolas", 8, "bold"),
                         text="BIO-RED")

    def _animate(self):
        if not self.winfo_exists():
            return
        self._line_y = (self._line_y + 4) % max(self._height, 1)
        self.coords(self._line_id, 0, self._line_y, self._width, self._line_y + 2)
        self.after(60, self._animate)


class StatusPill(tk.Canvas):
    """Píldora HUD (rounded) para paneles de detalle."""

    def __init__(self, master, text: str, accent: str = "#35E879", bg: str = "#0B1C12", **kwargs):
        super().__init__(master, height=26, highlightthickness=0, bd=0, bg=bg, **kwargs)
        self._bg = bg
        self._accent = accent
        self._text = text
        self._font = ("Segoe UI Variable", 9, "bold")
        self._pad_x = 12
        self._radius = 12
        self._draw()

    def set(self, text: str, accent: str | None = None):
        self._text = text
        if accent is not None:
            self._accent = accent
        self._draw()

    def _draw(self):
        self.delete("all")
        # Medición manual básica (aprox) para tamaño consistente.
        w = max(90, len(self._text) * 7 + self._pad_x * 2)
        self.configure(width=w)

        r = self._radius
        h = 26
        # rounded rect (polígono)
        points = [
            r, 0,
            w - r, 0,
            w, 0,
            w, r,
            w, h - r,
            w, h,
            w - r, h,
            r, h,
            0, h,
            0, h - r,
            0, r,
            0, 0,
        ]
        self.create_polygon(points, smooth=True, fill=self._bg, outline=self._accent, width=2)
        self.create_text(w // 2, 13, text=self._text, font=self._font, fill=self._accent)
