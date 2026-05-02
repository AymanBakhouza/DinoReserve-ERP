"""Helpers reutilizables para construir vistas CRUD."""
import tkinter as tk
from tkinter import ttk

from utils.constants import COLOR_BG, COLOR_BG_CARD, COLOR_BORDER, COLOR_TEXT, FONT_NORMAL
from utils.assets import find_background, load_photo_image
from views.theme import module_icon, module_system
from views.ui_kit import ScanlineOverlay, make_glass_toolbar


def make_section_header(parent, title: str, subtitle: str = "", module_key: str = "default") -> ttk.Frame:
    system = module_system(module_key)
    accent = system["accent"]
    neon = system["neon"]
    chip = system["chip"]
    icon = module_icon(module_key)
    header = ttk.Frame(parent, style="Card.TFrame", padding=(28, 22, 28, 18))
    header.pack(fill="x")
    bg_map = {
        "login": "bg_login.png",
        "dashboard": "bg_dashboard.png",
        "dinosaurs": "bg_dinosaurs.png",
        "reports": "bg_reports.png",
    }
    bg_name = bg_map.get(module_key, "bg_dashboard.png")
    bg_path = find_background(bg_name)
    hero = tk.Canvas(header, height=92, bg=COLOR_BG_CARD, highlightthickness=1, highlightbackground=COLOR_BORDER)
    hero.pack(fill="x", pady=(0, 12))
    def render_hero(event=None):
        width = max(420, hero.winfo_width())
        height = max(92, int(hero.cget("height")))
        hero.delete("all")
        if bg_path:
            bg_img = load_photo_image(bg_path, width=width, height=height)
            if bg_img:
                hero._bg_ref = bg_img
                hero.create_image(width // 2, height // 2, image=bg_img)
                hero.create_rectangle(0, 0, width, height, fill="#050706", stipple="gray50", outline="")
        for x in range(0, width + 20, 28):
            hero.create_line(x, 0, x, height - 8, fill="#17342C")
        for y in range(0, height - 8, 20):
            hero.create_line(0, y, width + 20, y, fill="#153128")
        hero.create_text(16, 22, anchor="w", fill=accent, font=("Bahnschrift", 15, "bold"),
                        text=f"SISTEMA {chip}")
        hero.create_text(16, 55, anchor="w", fill=neon, font=("Consolas", 10, "bold"),
                        text=f"CENTRO DE OPERACIONES DEL PARQUE · {chip}")
        chip_w = 130
        chip_x1 = width - chip_w - 24
        chip_x2 = width - 24
        icon_x = chip_x1 - 24
        hero.create_rectangle(chip_x1, 12, chip_x2, 38, fill="#0E1D19", outline=accent)
        hero.create_text((chip_x1 + chip_x2) // 2, 25, text=chip, fill=accent, font=("Consolas", 9, "bold"))
        hero.create_text(icon_x, 25, text=icon, fill=accent, font=("Segoe UI Emoji", 14))
    hero.bind("<Configure>", render_hero)
    render_hero()
    tk.Frame(header, bg=COLOR_BORDER, height=2).pack(fill="x", side="top", pady=(0, 12))
    scan = ScanlineOverlay(header, width=280, height=46, accent=accent)
    scan.pack(anchor="e", pady=(0, 10))
    ttk.Label(header, text=title, style="Title.TLabel").pack(anchor="w")
    if subtitle:
        ttk.Label(header, text=subtitle, style="Muted.TLabel").pack(
            anchor="w", pady=(4, 0)
        )
    return header


def make_toolbar(parent) -> ttk.Frame:
    bar = make_glass_toolbar(parent)
    bar.pack(fill="x")
    return bar


def make_treeview(parent, columns: list, height: int = 16) -> ttk.Treeview:
    """columns es lista de (key, label, width, anchor)."""
    container = ttk.Frame(parent, style="Card.TFrame", padding=(16, 8, 16, 16))
    container.pack(fill="both", expand=True)

    keys = [c[0] for c in columns]
    tree = ttk.Treeview(container, columns=keys, show="headings", height=height, style="Glow.Treeview")
    for key, label, width, anchor in columns:
        tree.heading(key, text=label)
        tree.column(key, width=width, anchor=anchor)

    sb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)
    return tree


class FormDialog(tk.Toplevel):
    """Diálogo modal con formulario dinámico.

    fields: lista de tuplas:
      (key, label, type, options)
        - type: 'entry' | 'combo' | 'spin' | 'text'
        - options: dict opcional con {values, from_, to, validate}
    """

    def __init__(self, parent, title: str, fields: list, initial: dict = None,
                 width: int = 520):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=COLOR_BG)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.result: dict | None = None
        self._field_defs = fields

        initial = initial or {}
        self._vars: dict[str, tk.Variable] = {}
        self._text_widgets: dict[str, tk.Text] = {}
        self._spin_bounds: dict[str, tuple[int, int]] = {}
        self._labels_by_key: dict[str, str] = {}

        wrap = ttk.Frame(self, padding=22)
        wrap.pack(fill="both", expand=True)

        ttk.Label(wrap, text=title, style="Subtitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )

        for i, (key, label, kind, opts) in enumerate(fields, start=1):
            self._labels_by_key[key] = label
            ttk.Label(wrap, text=label).grid(
                row=i, column=0, sticky="w", padx=(0, 12), pady=6
            )
            opts = opts or {}
            initial_val = initial.get(key, opts.get("default", ""))

            if kind == "combo":
                var = tk.StringVar(value=str(initial_val))
                combo = ttk.Combobox(
                    wrap, textvariable=var, state="readonly",
                    values=opts.get("values", []), width=32,
                )
                combo.grid(row=i, column=1, sticky="ew", pady=6)
                self._vars[key] = var
            elif kind == "spin":
                var = tk.StringVar(value=str(initial_val))
                min_v = int(opts.get("from_", 0))
                max_v = int(opts.get("to", 100))
                spin = ttk.Spinbox(
                    wrap, from_=min_v, to=max_v,
                    textvariable=var, width=12, justify="center",
                )
                if "validate" in opts:
                    spin.configure(
                        validate="key",
                        validatecommand=(self.register(opts["validate"]), "%P"),
                    )
                spin.grid(row=i, column=1, sticky="ew", pady=6)
                self._vars[key] = var
                self._spin_bounds[key] = (min_v, max_v)
            elif kind == "text":
                txt = tk.Text(
                    wrap, height=4, width=34,
                    bg=COLOR_BG_CARD, fg=COLOR_TEXT,
                    insertbackground=COLOR_TEXT,
                    font=FONT_NORMAL, borderwidth=0,
                )
                txt.insert("1.0", str(initial_val))
                txt.grid(row=i, column=1, sticky="ew", pady=6)
                self._text_widgets[key] = txt
            else:  # entry
                var = tk.StringVar(value=str(initial_val))
                entry = ttk.Entry(wrap, textvariable=var, width=36)
                if "validate" in opts:
                    entry.configure(
                        validate="key",
                        validatecommand=(self.register(opts["validate"]), "%P"),
                    )
                entry.grid(row=i, column=1, sticky="ew", pady=6)
                self._vars[key] = var

        wrap.columnconfigure(1, weight=1, minsize=width - 200)
        self._error_var = tk.StringVar(value="")
        ttk.Label(
            wrap,
            textvariable=self._error_var,
            style="Muted.TLabel",
            foreground="#ff6b6b",
            wraplength=width - 80,
        ).grid(row=len(fields) + 1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        # Botones
        btns = ttk.Frame(wrap)
        btns.grid(row=len(fields) + 2, column=0, columnspan=2,
                  sticky="e", pady=(18, 0))
        ttk.Button(btns, text="Cancelar", command=self._cancel).pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="Guardar", style="Accent.TButton",
                   command=self._save).pack(side="right")

        self.bind("<Escape>", lambda _e: self._cancel())
        self.update_idletasks()
        self._center_on_parent(parent)

    def _center_on_parent(self, parent):
        parent.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw - w) // 2
            y = py + (ph - h) // 2
        except tk.TclError:
            x, y = 200, 200
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    def _save(self):
        data = {k: v.get() for k, v in self._vars.items()}
        for k, w in self._text_widgets.items():
            data[k] = w.get("1.0", "end").strip()

        for key, label, _kind, opts in self._field_defs:
            options = opts or {}
            if options.get("required", True) and not str(data.get(key, "")).strip():
                self._error_var.set(f"El campo '{label}' es obligatorio.")
                return
        for key, (min_v, max_v) in self._spin_bounds.items():
            label = self._labels_by_key.get(key, key)
            raw = str(data.get(key, "")).strip()
            try:
                value = int(raw)
            except ValueError:
                self._error_var.set(
                    f"El campo '{label}' debe ser numérico y estar entre {min_v} y {max_v}."
                )
                return
            if value < min_v or value > max_v:
                self._error_var.set(
                    f"El campo '{label}' debe estar entre {min_v} y {max_v}."
                )
                return
            data[key] = value
        self._error_var.set("")
        self.result = data
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()
