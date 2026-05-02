# utils/assets.py
# Funciones para manejar recursos gráficos y rutas de archivos dentro de assets.
from __future__ import annotations

from pathlib import Path
import tkinter as tk

from utils.constants import ASSETS_DIR

try:
    from PIL import Image, ImageTk  # type: ignore
except Exception:  # pragma: no cover - Pillow es opcional
    Image = None
    ImageTk = None


def asset_path(*parts: str) -> Path:
    """Devuelve una ruta dentro del directorio assets."""
    return ASSETS_DIR.joinpath(*parts)


def load_photo_image(path: Path, width: int | None = None, height: int | None = None) -> tk.PhotoImage | None:
    """Carga imagen con fallback robusto (Pillow opcional)."""
    if not path.exists():
        return None
    if Image is not None and ImageTk is not None and width and height:
        try:
            img = Image.open(path).convert("RGBA")
            resample = getattr(Image, "Resampling", Image).LANCZOS
            img = img.resize((width, height), resample)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None
    try:
        img = tk.PhotoImage(file=str(path))
        if width and height:
            w = max(img.width(), 1)
            h = max(img.height(), 1)
            img = img.subsample(max(1, round(w / width)), max(1, round(h / height)))
        return img
    except tk.TclError:
        return None


def find_background(name: str) -> Path | None:
    """Busca fondos dentro de assets/backgrounds."""
    candidate = asset_path("backgrounds", name)
    return candidate if candidate.exists() else None
