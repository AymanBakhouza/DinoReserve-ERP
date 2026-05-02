"""Ventana principal con shell Neo-Jurassic HUD."""
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from controllers.dashboard_controller import DashboardController
from services.inventory_service import InventoryService
from services.report_service import ReportService
from utils.constants import (
    APP_NAME,
    APP_VERSION,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_BG,
    COLOR_BG_ALT,
    COLOR_BG_CARD,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_WARNING,
    FONT_NORMAL,
)
from utils.logger import get_logger
from views.dinosaur_view import DinosaurView
from views.employee_view import EmployeeView
from views.enclosure_view import EnclosureView
from views.inventory_view import InventoryView
from views.maintenance_view import MaintenanceView
from views.reports_view import ReportsView
from views.styles import configure_styles
from views.ticket_view import TicketView
from views.ui_kit import draw_kpi_tile, load_brand_logo, make_status_pill, style_nav_button
from utils.assets import find_background, load_photo_image
from views.ui_kit import StatusPill


class DashboardView(tk.Tk):
    """Ventana raíz tras el login. Navegación lateral + panel central."""

    NAV_ITEMS = [
        ("home",        "Inicio"),
        ("dinosaurs",   "Dinosaurios"),
        ("enclosures",  "Recintos"),
        ("tickets",     "Taquilla"),
        ("employees",   "Empleados"),
        ("inventory",   "Inventario"),
        ("maintenance", "Mantenimiento"),
        ("reports",     "Reportes"),
        ("events",      "Eventos"),
        ("logs",        "Registros"),
    ]
    EVENT_LABELS = {
        "tropical_storm": "Tormenta",
        "feeding_delay": "Alimentación",
        "stock_variation": "Existencias",
        "fence_malfunction": "Valla",
        "dinosaur_health_alert": "Salud",
        "calm_day": "Calma",
    }
    SEVERITY_LABELS = {
        "INFO": "Informativo",
        "WARNING": "Advertencia",
        "ERROR": "Error",
    }
    SEVERITY_VALUES = {label: code for code, label in SEVERITY_LABELS.items()}
    LEVEL_VALUES = {
        "Todos": None,
        "Informativo": "INFO",
        "Advertencia": "WARNING",
        "Error": "ERROR",
    }

    def __init__(self, current_user: dict):
        super().__init__()
        self.user = current_user
        self.controller = DashboardController(current_user)
        self._log = get_logger()
        self._nav_buttons: dict[str, ttk.Button] = {}
        self._active_view = "home"
        self._logo_img = load_brand_logo(72, 72)
        self._hero_logo_img = load_brand_logo(92, 92)
        self._pulse_step = 0
        self._status_chip: ttk.Label | None = None
        self._clock_label: ttk.Label | None = None
        self._clock_job = None
        self._hud_job = None
        self._kpi_cards: list[ttk.Frame] = []
        self._kpi_pulse = 0
        self._hero_bg = None
        self._home_occ_rows = []
        self._home_recent_events = []
        self.logged_out = False
        self._log_query = tk.StringVar()
        self._log_level = tk.StringVar(value="Todos")
        self._log_text: tk.Text | None = None
        self._log_lines: list[str] = []
        self._log_traces_bound = False

        self.title(f"{APP_NAME} — Panel principal")
        self.geometry("1400x850")
        self.minsize(1200, 760)
        self.configure(bg=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        configure_styles(self)

        self._build_ui()
        self._navigate("home")
        self._animate_hud()

    # ------------------------------------------------------------
    def _build_ui(self):
        # Barra lateral
        sidebar = tk.Frame(self, bg=COLOR_BG_ALT, width=282)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Frame(sidebar, bg=COLOR_PRIMARY, height=3).pack(fill="x")
        brand = tk.Frame(sidebar, bg=COLOR_BG_ALT)
        brand.pack(fill="x", pady=(26, 8), padx=24)
        if self._logo_img:
            tk.Label(brand, image=self._logo_img, bg=COLOR_BG_ALT).pack(anchor="center")
        else:
            tk.Label(brand, text="DR", bg=COLOR_BG_ALT,
                     fg=COLOR_PRIMARY, font=("Segoe UI", 26, "bold")).pack(anchor="center")

        tk.Label(
            sidebar,
            text="DINORESERVE",
            bg=COLOR_BG_ALT,
            fg=COLOR_TEXT,
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", padx=22, pady=(8, 2))
        tk.Label(
            sidebar,
            text="SISTEMA DE RESERVA JURÁSICA",
            bg=COLOR_BG_ALT,
            fg=COLOR_PRIMARY,
            font=("Consolas", 9, "bold"),
        ).pack(anchor="w", padx=22, pady=(0, 18))

        operator = tk.Frame(sidebar, bg=COLOR_BG_CARD, highlightthickness=1, highlightbackground=COLOR_BORDER)
        operator.pack(fill="x", padx=18, pady=(0, 18))
        tk.Label(operator, text="OPERADOR ACTIVO", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MUTED,
                 font=("Consolas", 8, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(operator, text=f"{self.user['username']} / {self._role_label(self.user['role'])}",
                 bg=COLOR_BG_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(0, 10))

        # Botones de navegación
        for idx, (key, label) in enumerate(self.NAV_ITEMS, start=1):
            btn = ttk.Button(
                sidebar, text=f"{idx:02d}  {label.upper()}", style="Nav.TButton",
                command=lambda k=key: self._navigate(k),
            )
            btn.pack(fill="x", padx=18, pady=3)
            self._nav_buttons[key] = btn

        # Salir
        ttk.Button(
            sidebar, text="Cerrar sesión",
            style="Nav.TButton",
            command=self._logout,
        ).pack(fill="x", padx=12, pady=(40, 12), side="bottom")
        tk.Label(
            sidebar,
            text=f"VERSIÓN DE COMANDO v{APP_VERSION}",
            bg=COLOR_BG_ALT,
            fg=COLOR_TEXT_MUTED,
            font=("Consolas", 9, "bold"),
        ).pack(side="bottom", pady=(0, 10))

        # Contenedor principal
        self.main_area = tk.Frame(self, bg=COLOR_BG)
        self.main_area.pack(side="left", fill="both", expand=True)

    # ------------------------------------------------------------
    def _clear_main(self):
        try:
            self.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass
        if self._clock_job is not None:
            try:
                self.after_cancel(self._clock_job)
            except tk.TclError:
                pass
            self._clock_job = None
        self._kpi_cards = []
        self._status_chip = None
        self._clock_label = None
        for w in self.main_area.winfo_children():
            w.destroy()

    def _role_label(self, role: str) -> str:
        labels = {
            "admin": "administrador",
            "operator": "operador",
            "operador": "operador",
        }
        return labels.get(str(role).lower(), str(role))

    def _make_scrollable_page(self) -> tk.Frame:
        shell = tk.Frame(self.main_area, bg=COLOR_BG)
        shell.pack(fill="both", expand=True)

        canvas = tk.Canvas(shell, bg=COLOR_BG, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(shell, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=COLOR_BG)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def refresh_scrollregion(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_width(event):
            canvas.itemconfigure(window_id, width=event.width)
            refresh_scrollregion()

        def wheel(event):
            if isinstance(event.widget, (tk.Text, ttk.Treeview)):
                return
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        content.bind("<Configure>", refresh_scrollregion)
        canvas.bind("<Configure>", fit_width)
        for widget in (canvas, content):
            widget.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", wheel))
            widget.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return content

    def _navigate(self, key: str):
        self._active_view = key
        for nav_key, button in self._nav_buttons.items():
            style_nav_button(button, nav_key == key)
        self._clear_main()
        accent_map = {
            "home": COLOR_PRIMARY,
            "dinosaurs": COLOR_SUCCESS,
            "enclosures": COLOR_DANGER,
            "tickets": "#FFB84D",
            "employees": "#9BD26D",
            "inventory": "#7FE7A8",
            "maintenance": COLOR_DANGER,
            "reports": "#C6B26A",
            "events": "#FFB84D",
            "logs": COLOR_PRIMARY,
        }
        strip = tk.Frame(self.main_area, bg=accent_map.get(key, COLOR_PRIMARY), height=4)
        strip.pack(fill="x", side="top")
        content = self._make_scrollable_page()
        if key == "home":
            self._show_home(content)
        elif key == "dinosaurs":
            DinosaurView(content).pack(fill="both", expand=True)
        elif key == "enclosures":
            EnclosureView(content).pack(fill="both", expand=True)
        elif key == "tickets":
            TicketView(content).pack(fill="both", expand=True)
        elif key == "employees":
            EmployeeView(content).pack(fill="both", expand=True)
        elif key == "inventory":
            InventoryView(content).pack(fill="both", expand=True)
        elif key == "maintenance":
            MaintenanceView(content).pack(fill="both", expand=True)
        elif key == "reports":
            ReportsView(content).pack(fill="both", expand=True)
        elif key == "events":
            self._show_events(content)
        elif key == "logs":
            self._show_logs(content)

    # ------------------------------------------------------------
    def _show_home(self, parent=None):
        target = parent or self.main_area
        rs = ReportService()
        invs = InventoryService()
        from database.connection import DatabaseConnection

        topbar = tk.Frame(target, bg=COLOR_BG, padx=30, pady=14)
        topbar.pack(fill="x")
        tk.Label(
            topbar,
            text="BIOCOMANDO / TELEMETRÍA DEL PARQUE EN VIVO",
            bg=COLOR_BG,
            fg=COLOR_PRIMARY,
            font=("Consolas", 10, "bold"),
        ).pack(side="left")
        self._clock_label = ttk.Label(topbar, text="", style="Muted.TLabel")
        self._clock_label.pack(side="right")
        self._update_clock()

        # Bienvenida
        header = ttk.Frame(target, padding=(30, 6, 30, 8))
        header.pack(fill="x")
        hero = tk.Canvas(header, height=178, bg=COLOR_BG_ALT, highlightthickness=1, highlightbackground=COLOR_BORDER)
        hero.pack(fill="x", pady=(0, 12))
        hero.bind("<Configure>", lambda e: self._render_home_hero(hero, e.width, e.height))

        row = ttk.Frame(header)
        row.pack(fill="x")
        left = ttk.Frame(row)
        left.pack(side="left")
        tk.Label(left, text="Centro de Misión", bg=COLOR_BG, fg=COLOR_TEXT,
                 font=("Segoe UI", 29, "bold")).pack(anchor="w")
        tk.Label(
            left,
            text=f"Operador {self.user['username']} conectado · telemetría predictiva del parque activa",
            bg=COLOR_BG,
            fg=COLOR_TEXT_MUTED,
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(4, 0))
        right = ttk.Frame(row)
        right.pack(side="right")
        self._status_chip = make_status_pill(right, "SISTEMA EN LÍNEA")
        self._status_chip.pack(anchor="e")

        # Tarjetas KPI
        kpi_frame = ttk.Frame(target, padding=(26, 8, 26, 12))
        kpi_frame.pack(fill="x")

        try:
            revenue = rs.daily_revenue()
            tickets_today = rs.daily_tickets_count()
            low = invs.list_low_stock()
            danger_rows = rs.avg_danger_by_enclosure()
            maintenance_rows = rs.maintenance_by_status()
            occ_rows = rs.occupation_by_zone()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self._home_occ_rows = occ_rows

        recintos_activos = len([r for r in occ_rows if r["max_capacity"] and r["occupancy"] >= 0])
        dino_alerta = len([r for r in danger_rows if (r["avg_danger"] or 0) >= 4])
        maint_pending = sum(r["quantity"] for r in maintenance_rows if r["status"] in {"pending", "in_progress"})

        cards = [
            ("Ingresos de hoy", f"€ {revenue:,.2f}", COLOR_SUCCESS),
            ("Entradas registradas", str(tickets_today), COLOR_PRIMARY),
            ("Alertas de suministros", str(len(low)),
             COLOR_DANGER if low else COLOR_SUCCESS),
            ("Biomas activos", str(recintos_activos), "#9BD26D"),
            ("Señales de riesgo biológico", str(dino_alerta), COLOR_WARNING),
            ("Cola de reparaciones", str(maint_pending), COLOR_DANGER),
        ]
        self._kpi_cards = []
        for i, (lbl, val, color) in enumerate(cards):
            row_idx = i // 3
            col_idx = i % 3
            kpi_frame.columnconfigure(col_idx, weight=1)
            card = draw_kpi_tile(kpi_frame, lbl, val, color)
            card.grid(row=row_idx, column=col_idx, sticky="nsew", padx=8, pady=5, ipady=2)
            self._kpi_cards.append(card)

        action_row = tk.Frame(target, bg=COLOR_BG_CARD, highlightthickness=1, highlightbackground=COLOR_BORDER)
        action_row.pack(fill="x", padx=30, pady=(2, 12))
        tk.Frame(action_row, bg=COLOR_ACCENT, width=4).pack(side="left", fill="y")
        tk.Label(action_row, text="EJECUCIÓN RÁPIDA", bg=COLOR_BG_CARD, fg=COLOR_PRIMARY,
                 font=("Consolas", 10, "bold")).pack(side="left", padx=(18, 16), pady=14)
        ttk.Button(action_row, text="Vender entrada", style="Accent.TButton",
                   command=lambda: self._navigate("tickets")).pack(side="left", padx=8)
        ttk.Button(action_row, text="Simular evento", command=self._fire_event).pack(side="left", padx=8)
        ttk.Button(action_row, text="Ver suministros", command=lambda: self._navigate("inventory")).pack(side="left", padx=8)

        # Main operations board (left/right)
        board = ttk.Frame(target, padding=(30, 0, 30, 14))
        board.pack(fill="both", expand=True)
        board.columnconfigure(0, weight=3)
        board.columnconfigure(1, weight=2)

        left = tk.Frame(board, bg=COLOR_BG_CARD, highlightthickness=1, highlightbackground=COLOR_BORDER, padx=16, pady=14)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = tk.Frame(board, bg=COLOR_BG_CARD, highlightthickness=1, highlightbackground=COLOR_BORDER, padx=16, pady=14)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(left, text="Matriz de capacidad de biomas", bg=COLOR_BG_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        occ_canvas = tk.Canvas(left, height=280, bg="#09180F", highlightthickness=1, highlightbackground=COLOR_BORDER)
        occ_canvas.pack(fill="x", pady=(8, 0))
        occ_canvas.bind("<Configure>", lambda e: self._draw_capacity_bars(occ_canvas, self._home_occ_rows, e.width, e.height))

        tk.Label(right, text="Cronología de señales de incidentes", bg=COLOR_BG_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        timeline = tk.Canvas(right, height=130, bg="#09180F", highlightthickness=1, highlightbackground=COLOR_BORDER)
        timeline.pack(fill="x", pady=(8, 10))
        recent_events = []
        with DatabaseConnection().cursor() as cur:
            cur.execute(
                """SELECT created_at, event_type, severity, description
                     FROM random_events
                    ORDER BY id DESC LIMIT 6"""
            )
            recent_events = cur.fetchall()
        self._home_recent_events = recent_events
        timeline.bind("<Configure>", lambda e: self._draw_event_timeline(timeline, self._home_recent_events, e.width, e.height))

        tk.Label(right, text="Flujo de operaciones", bg=COLOR_BG_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        alert_box = tk.Text(
            right,
            height=8,
            bg="#09180F",
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            borderwidth=0,
            padx=10,
            pady=10,
            font=("Consolas", 9),
        )
        alert_box.pack(fill="both", expand=True, pady=(8, 0))
        alert_box.insert("1.0", self._build_alert_console(low, recent_events))
        alert_box.configure(state="disabled")

        # Aviso de stock bajo
        if low:
            warn = tk.Frame(target, bg="#2C2110")
            warn.pack(fill="x", padx=30, pady=(0, 18))
            tk.Label(
                warn,
                text=f"ALERTA DE SUMINISTROS · {len(low)} ítem(s) por debajo del mínimo · Abre suministros",
                bg="#2C2110", fg=COLOR_WARNING,
                font=("Consolas", 10, "bold"),
            ).pack(padx=16, pady=10)

    def _draw_capacity_bars(self, canvas: tk.Canvas, rows, width: int | None = None, height: int | None = None):
        canvas.delete("all")
        width = width or canvas.winfo_width() or 860
        height = height or int(canvas.cget("height")) or 280
        if width < 120:
            return
        for gx in range(20, width, 42):
            canvas.create_line(gx, 10, gx, height - 10, fill="#143322")
        for gy in range(10, height, 22):
            canvas.create_line(20, gy, width - 20, gy, fill="#102719")

        y = 24
        for row in rows[:7]:
            name = str(row["name"])
            occ = int(row["occupancy"])
            mx = int(row["max_capacity"]) if row["max_capacity"] else 1
            ratio = max(0.0, min(1.0, occ / mx))
            pct = ratio * 100
            color = COLOR_SUCCESS if pct < 70 else COLOR_WARNING if pct < 90 else COLOR_DANGER
            canvas.create_text(28, y + 8, anchor="w", fill=COLOR_TEXT, font=("Segoe UI", 10, "bold"), text=name[:24])
            data_x = min(max(int(width * 0.36), 220), width - 220)
            canvas.create_text(data_x, y + 8, anchor="w", fill=COLOR_TEXT_MUTED, font=("Consolas", 9), text=f"{occ}/{mx} · {pct:.0f}%")
            x1 = min(max(int(width * 0.52), data_x + 120), width - 160)
            x2 = width - 24
            canvas.create_rectangle(x1, y + 2, x2, y + 16, fill="#0B1C12", outline=COLOR_BORDER)
            fill = int((x2 - x1) * ratio)
            canvas.create_rectangle(x1, y + 2, x1 + fill, y + 16, fill="#1A472B", outline=color, width=1)
            canvas.create_rectangle(x1, y + 2, x1 + min(fill, 20), y + 16, fill=color, outline="")
            y += 34

    def _draw_event_timeline(self, canvas: tk.Canvas, events, width: int | None = None, height: int | None = None):
        canvas.delete("all")
        width = width or canvas.winfo_width() or 520
        height = height or int(canvas.cget("height")) or 130
        if width < 120:
            return
        top_y = max(22, int(height * 0.2))
        canvas.create_line(30, top_y, width - 26, top_y, fill=COLOR_BORDER, width=2)
        x = 30
        step = max(68, int((width - 80) / max(1, len(events))))
        for ev in events:
            sev = str(ev["severity"]).upper()
            color = {"INFO": COLOR_SUCCESS, "WARNING": COLOR_WARNING, "ERROR": COLOR_DANGER}.get(sev, COLOR_PRIMARY)
            canvas.create_oval(x - 6, top_y - 6, x + 6, top_y + 6, fill=color, outline="")
            canvas.create_text(x, top_y + 20, text={"INFO": "I", "WARNING": "A", "ERROR": "E"}.get(sev, sev[:1]), fill=color, font=("Consolas", 10, "bold"))
            label = self.EVENT_LABELS.get(str(ev["event_type"]), str(ev["event_type"]))
            canvas.create_text(x, top_y + 38, text=label[:12], fill=COLOR_TEXT_MUTED, font=("Consolas", 8))
            x += step

    def _build_alert_console(self, low_items, events):
        lines = []
        lines.append(">> FLUJO DE OPERACIONES DEL PARQUE")
        lines.append("")
        if low_items:
            lines.append(f"[SUMINISTROS] {len(low_items)} señal(es) de existencias bajas detectadas.")
        else:
            lines.append("[SUMINISTROS] Inventario en estado nominal.")
        for ev in events[:4]:
            sev = str(ev["severity"]).upper()
            label = self.EVENT_LABELS.get(str(ev["event_type"]), str(ev["event_type"]))
            sev_label = self.SEVERITY_LABELS.get(sev, sev).upper()
            lines.append(f"[{sev_label}] {label}: {str(ev['description'])[:64]}")
        lines.append("")
        lines.append(">> FIN DE LA TRANSMISIÓN")
        return "\n".join(lines)

    def _render_home_hero(self, canvas: tk.Canvas, width: int, height: int):
        if width < 120:
            return
        canvas.delete("all")
        canvas.create_rectangle(0, 0, width, height, fill=COLOR_BG_ALT, outline="")
        bands = ["#06110B", "#09180F", "#0B1C12", "#102719", "#173A27"]
        for i, color in enumerate(bands):
            canvas.create_rectangle(0, int(height * i / len(bands)), width, int(height * (i + 1) / len(bands)), fill=color, outline="")
        for x in range(0, width, 42):
            canvas.create_line(x, 0, x + 70, height, fill="#173A27")
        for y in range(0, height, 30):
            canvas.create_line(0, y, width, y, fill="#143322")
        bg_path = find_background("bg_dashboard.png")
        if bg_path:
            self._hero_bg = load_photo_image(bg_path, width=max(120, width), height=max(90, height))
            if self._hero_bg:
                canvas.create_image(width // 2, height // 2, image=self._hero_bg)
                canvas.create_rectangle(0, 0, width, height, fill=COLOR_BG, stipple="gray75", outline="")

        orbit_x = width - 185
        orbit_y = height // 2
        for r, color in [(84, COLOR_BORDER), (58, COLOR_PRIMARY), (34, COLOR_ACCENT)]:
            canvas.create_oval(orbit_x - r, orbit_y - r, orbit_x + r, orbit_y + r, outline=color, width=1)
        canvas.create_line(orbit_x - 112, orbit_y, orbit_x + 112, orbit_y, fill=COLOR_BORDER)
        canvas.create_line(orbit_x, orbit_y - 92, orbit_x, orbit_y + 92, fill=COLOR_BORDER)

        title_size = max(24, min(42, int(width * 0.028)))
        text_size = max(10, min(15, int(width * 0.012)))
        tag_size = max(8, min(10, int(width * 0.0088)))
        canvas.create_text(34, 32, anchor="w", fill=COLOR_PRIMARY, font=("Segoe UI", 11, "bold"),
                         text="BIOCOMANDO DINORESERVE")
        canvas.create_text(34, 66, anchor="w", fill=COLOR_TEXT, font=("Segoe UI", title_size, "bold"),
                         text="Red de Sistemas Jurásicos")
        canvas.create_text(36, 116, anchor="w", fill=COLOR_TEXT_MUTED, font=("Segoe UI", text_size),
                         text="Operaciones predictivas para hábitats, bio-riesgo, suministros e ingresos.")
        canvas.create_text(36, 146, anchor="w", fill=COLOR_SUCCESS, font=("Consolas", tag_size, "bold"),
                         text="SINCRONÍA: EN VIVO   BIO-RED: ESTABLE   SEGURIDAD: MONITORIZADA")
        if self._hero_logo_img:
            canvas.create_image(orbit_x, orbit_y, image=self._hero_logo_img)
        canvas.create_rectangle(18, 18, width - 20, height - 18, outline=COLOR_BORDER, width=1)
        canvas.create_line(18, 18, min(width - 20, 420), 18, fill=COLOR_PRIMARY, width=3)
        canvas.create_line(width - 360, height - 18, width - 20, height - 18, fill=COLOR_ACCENT, width=3)

    def _draw_radar_grid(self, canvas: tk.Canvas, width: int, height: int):
        for x in range(0, width, 24):
            canvas.create_line(x, 0, x, height, fill="#17342C")
        for y in range(0, height, 20):
            canvas.create_line(0, y, width, y, fill="#153128")

    def _animate_hud(self):
        """Pequeño pulso visual para dar sensación de HUD activo."""
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        self._pulse_step = (self._pulse_step + 1) % 4
        if self._status_chip and self._status_chip.winfo_exists():
            colors = [COLOR_PRIMARY, COLOR_ACCENT_HOVER, COLOR_SUCCESS, COLOR_TEXT_MUTED]
            self._status_chip.configure(foreground=colors[self._pulse_step])
        if self._kpi_cards:
            self._kpi_pulse = (self._kpi_pulse + 1) % (len(self._kpi_cards) * 2)
            active_idx = self._kpi_pulse // 2
            for idx, card in enumerate(self._kpi_cards):
                if not card.winfo_exists():
                    continue
                if hasattr(card, "configure"):
                    card.configure(highlightbackground=COLOR_BORDER)
                if idx == active_idx:
                    card.configure(highlightbackground=COLOR_PRIMARY)
        try:
            self._hud_job = self.after(500, self._animate_hud)
        except tk.TclError:
            pass

    def _update_clock(self):
        try:
            if not self.winfo_exists():
                return
            if self._clock_label and self._clock_label.winfo_exists():
                self._clock_label.configure(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            self._clock_job = self.after(1000, self._update_clock)
        except tk.TclError:
            pass

    # ------------------------------------------------------------
    def _show_events(self, parent=None):
        target = parent or self.main_area
        wrap = ttk.Frame(target, padding=28)
        wrap.pack(fill="both", expand=True)
        ttk.Label(wrap, text="Motor de eventos aleatorios",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            wrap,
            text=("Los eventos simulan situaciones reales del parque "
                  "(tormentas, retrasos, fallos…). Cada disparo afecta a la "
                  "base de datos, queda en log_parque.txt y se registra en la "
                  "tabla random_events."),
            style="Muted.TLabel", wraplength=900, justify="left",
        ).pack(anchor="w", pady=(6, 18))

        actions = ttk.Frame(wrap)
        actions.pack(anchor="w")
        self._event_severity = tk.StringVar(value="Todos")
        ttk.Combobox(actions, textvariable=self._event_severity, state="readonly",
                     values=["Todos", *self.SEVERITY_LABELS.values()], width=14).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="🎲  Lanzar evento aleatorio",
                   style="Accent.TButton",
                   command=self._fire_event).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="🔄  Lanzar 5 eventos",
                   command=lambda: [self._fire_event() for _ in range(5)]).pack(side="left")
        ttk.Button(actions, text="↻ Refrescar historial", command=self._refresh_events_table).pack(side="left", padx=(8, 0))

        # Lista histórica
        ttk.Label(wrap, text="Historial reciente",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(24, 8))

        self._events_tree = ttk.Treeview(
            wrap,
            columns=("date", "type", "severity", "description"),
            show="headings", height=14,
        )
        self._events_tree.tag_configure("INFO", foreground="#9fc9af")
        self._events_tree.tag_configure("WARNING", foreground="#ffd54f")
        self._events_tree.tag_configure("ERROR", foreground="#ff6b6b")
        for col, txt, w, anchor in [
            ("date", "Fecha", 160, "w"),
            ("type", "Tipo", 180, "w"),
            ("severity", "Gravedad", 130, "center"),
            ("description", "Descripción", 600, "w"),
        ]:
            self._events_tree.heading(col, text=txt)
            self._events_tree.column(col, width=w, anchor=anchor)
        self._events_tree.pack(fill="both", expand=True)
        self._events_tree.bind("<<TreeviewSelect>>", lambda _e: self._render_event_detail())

        self._event_detail = ttk.Frame(wrap, style="Card.TFrame", padding=(16, 12))
        self._event_detail.pack(fill="x", pady=(12, 0))
        ttk.Label(self._event_detail, text="Detalle del incidente", style="Subtitle.TLabel").pack(anchor="w")
        row = ttk.Frame(self._event_detail, style="Card.TFrame")
        row.pack(anchor="w", pady=(8, 0))
        self._pill_event_sev = StatusPill(row, "GRAVEDAD: —", accent="#7FE7F5")
        self._pill_event_sev.pack(side="left", padx=(0, 10))
        self._pill_event_type = StatusPill(row, "TIPO: —", accent="#D9A441")
        self._pill_event_type.pack(side="left")
        self._event_detail_text = ttk.Label(self._event_detail, text="Selecciona un evento para ver detalles.", style="Muted.TLabel")
        self._event_detail_text.pack(anchor="w", pady=(8, 0))
        self._event_desc_cache = ""
        ttk.Button(
            self._event_detail,
            text="Copiar descripción",
            command=self._copy_event_description,
        ).pack(anchor="w", pady=(10, 0))

        self._refresh_events_table()

    def _fire_event(self):
        result = self.controller.trigger_random_event()
        # Notificación GUI
        icons = {"info": ("ℹ", "Información"), "warning": ("⚠", "Advertencia"),
                 "error": ("⛔", "Crítico")}
        icon, _label = icons.get(result.severity, ("ℹ", "Información"))
        sev_label = self.SEVERITY_LABELS.get(result.severity.upper(), result.severity)
        messagebox.showinfo(
            f"{icon}  {result.title}",
            f"{result.description}\n\nGravedad: {sev_label}",
            parent=self,
        )
        if hasattr(self, "_events_tree") and self._events_tree.winfo_exists():
            self._refresh_events_table()

    def _refresh_events_table(self):
        from database.connection import DatabaseConnection
        for i in self._events_tree.get_children():
            self._events_tree.delete(i)
        with DatabaseConnection().cursor() as cur:
            cur.execute(
                """SELECT created_at, event_type, severity, description
                     FROM random_events
                    ORDER BY id DESC LIMIT 100"""
            )
            for row in cur.fetchall():
                selected = getattr(self, "_event_severity", None)
                selected_code = self.LEVEL_VALUES.get(selected.get()) if selected else None
                if selected_code and row["severity"].upper() != selected_code:
                    continue
                sev = row["severity"].upper()
                self._events_tree.insert(
                    "", "end",
                    values=(row["created_at"], self.EVENT_LABELS.get(str(row["event_type"]), row["event_type"]),
                            self.SEVERITY_LABELS.get(sev, sev), row["description"]),
                    tags=(sev,),
                )
        self._render_event_detail()

    def _render_event_detail(self):
        if not hasattr(self, "_events_tree") or not self._events_tree.winfo_exists():
            return
        sel = self._events_tree.selection()
        if not sel:
            self._pill_event_sev.set("GRAVEDAD: —", accent="#7FE7F5")
            self._pill_event_type.set("TIPO: —", accent="#D9A441")
            self._event_detail_text.configure(text="Selecciona un evento para ver detalles.")
            return
        vals = self._events_tree.item(sel[0]).get("values", [])
        try:
            date, etype, sev, desc = vals
        except Exception:
            return
        sev_u = self.SEVERITY_VALUES.get(str(sev), str(sev)).upper()
        sev_color = {"INFO": "#59F3BE", "WARNING": "#F4D27C", "ERROR": "#FF7D7A"}.get(sev_u, "#7FE7F5")
        sev_label = {"INFO": "INFORMATIVO", "WARNING": "ADVERTENCIA", "ERROR": "ERROR"}.get(sev_u, sev_u)
        self._pill_event_sev.set(f"GRAVEDAD: {sev_label}", accent=sev_color)
        self._pill_event_type.set(f"TIPO: {etype}", accent="#D9A441")
        self._event_detail_text.configure(text=f"{date} · {desc}")
        self._event_desc_cache = str(desc)

    def _copy_event_description(self):
        text = getattr(self, "_event_desc_cache", "")
        if not text:
            return
        self.clipboard_clear()
        self.clipboard_append(text)

    # ------------------------------------------------------------
    def _show_logs(self, parent=None):
        from utils.constants import DB_PATH, LOG_PATH
        target = parent or self.main_area
        wrap = ttk.Frame(target, padding=28)
        wrap.pack(fill="both", expand=True)
        ttk.Label(wrap, text="Registros del sistema",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(wrap, text=f"Archivo: {LOG_PATH}",
                  style="Muted.TLabel").pack(anchor="w", pady=(4, 14))
        ttk.Label(
            wrap,
            text=f"Base de datos activa: {DB_PATH.name}",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 2))
        ttk.Label(
            wrap,
            text=f"Ruta DB: {DB_PATH}",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 12))
        filters = ttk.Frame(wrap)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Entry(filters, textvariable=self._log_query, width=36).pack(side="left")
        level_combo = ttk.Combobox(filters, textvariable=self._log_level, state="readonly",
                                   values=list(self.LEVEL_VALUES.keys()), width=14)
        level_combo.pack(side="left", padx=8)
        ttk.Button(filters, text="Aplicar filtros", command=self._populate_logs).pack(side="left")

        text = tk.Text(
            wrap, bg=COLOR_BG_CARD, fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            font=("Consolas", 10), borderwidth=0, padx=12, pady=12,
        )
        self._log_text = text
        sb = ttk.Scrollbar(wrap, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)
        text.bind("<ButtonRelease-1>", lambda _e: self._render_log_detail(text))
        text.bind("<KeyRelease>", lambda _e: self._render_log_detail(text))

        try:
            content = LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else ""
        except Exception as exc:
            content = f"No se pudo leer el log: {exc}"
        self._log_lines = content.splitlines()

        buttons = ttk.Frame(wrap)
        buttons.pack(anchor="w", pady=(12, 0))
        ttk.Button(buttons, text="🔄  Refrescar", command=self._reload_logs).pack(side="left")
        ttk.Button(
            buttons,
            text="Copiar",
            command=lambda: (self.clipboard_clear(), self.clipboard_append(text.get("1.0", "end"))),
        ).pack(side="left", padx=8)
        ttk.Button(
            buttons,
            text="Copiar línea",
            command=lambda: self._copy_selected_log_line(text),
        ).pack(side="left", padx=8)
        ttk.Button(
            buttons,
            text="Copiar ruta de base de datos",
            command=lambda: (self.clipboard_clear(), self.clipboard_append(str(DB_PATH))),
        ).pack(side="left", padx=8)

        self._log_detail = ttk.Frame(wrap, style="Card.TFrame", padding=(16, 12))
        self._log_detail.pack(fill="x", pady=(12, 0))
        ttk.Label(self._log_detail, text="Detalle de log", style="Subtitle.TLabel").pack(anchor="w")
        row = ttk.Frame(self._log_detail, style="Card.TFrame")
        row.pack(anchor="w", pady=(8, 0))
        self._pill_log_level = StatusPill(row, "NIVEL: —", accent="#7FE7F5")
        self._pill_log_level.pack(side="left", padx=(0, 10))
        self._pill_log_stats = StatusPill(row, "LÍNEAS: —", accent="#D9A441")
        self._pill_log_stats.pack(side="left")
        self._log_detail_text = ttk.Label(self._log_detail, text="Haz click en una línea para ver el nivel detectado.", style="Muted.TLabel")
        self._log_detail_text.pack(anchor="w", pady=(8, 0))
        if not self._log_traces_bound:
            self._log_query.trace_add("write", lambda *_: self._populate_logs())
            self._log_level.trace_add("write", lambda *_: self._populate_logs())
            self._log_traces_bound = True
        self._populate_logs()

    def _reload_logs(self):
        from utils.constants import LOG_PATH
        try:
            content = LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else ""
        except Exception as exc:
            content = f"No se pudo leer el log: {exc}"
        self._log_lines = content.splitlines()
        self._populate_logs()

    def _populate_logs(self):
        text = getattr(self, "_log_text", None)
        if text is None or not text.winfo_exists():
            return
        query = self._log_query.get().strip().lower()
        level = self.LEVEL_VALUES.get(self._log_level.get())
        filtered = []
        for line in self._log_lines:
            upper_line = line.upper()
            if query and query not in line.lower():
                continue
            if level and level not in upper_line:
                continue
            filtered.append(line)
        text.configure(state="normal")
        text.delete("1.0", "end")
        text.insert("1.0", "\n".join(filtered)[-200_000:])
        text.see("end")
        if hasattr(self, "_pill_log_stats") and self._pill_log_stats.winfo_exists():
            self._pill_log_stats.set(f"LÍNEAS: {len(filtered)}", accent="#D9A441")

    def _copy_selected_log_line(self, text_widget: tk.Text):
        try:
            line = text_widget.get("insert linestart", "insert lineend").strip()
        except Exception:
            return
        if not line:
            return
        self.clipboard_clear()
        self.clipboard_append(line)

    def _render_log_detail(self, text_widget: tk.Text):
        try:
            line = text_widget.get("insert linestart", "insert lineend")
        except Exception:
            return
        upper = line.upper()
        if "ERROR" in upper:
            self._pill_log_level.set("NIVEL: ERROR", accent="#FF7D7A")
        elif "WARNING" in upper or "WARN" in upper:
            self._pill_log_level.set("NIVEL: ADVERTENCIA", accent="#F4D27C")
        elif "INFO" in upper:
            self._pill_log_level.set("NIVEL: INFORMATIVO", accent="#59F3BE")
        else:
            self._pill_log_level.set("NIVEL: —", accent="#7FE7F5")
        self._log_detail_text.configure(text=line.strip() or "—")

    # ------------------------------------------------------------
    def _logout(self):
        if messagebox.askyesno("Cerrar sesión",
                               "¿Seguro que quieres cerrar la sesión?",
                               parent=self):
            self.logged_out = True
            self._log.info("Cerró sesión: %s", self.user['username'])
            self.destroy()
