"""Vista de Reportes con pestañas y SQL JOIN/GROUP BY/SUM/AVG."""
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csv

from services.report_service import ReportService
from views.ui_kit import make_status_pill

TICKET_LABELS = {
    "normal": "Normal",
    "child": "Infantil",
    "vip": "VIP",
    "fast_pass": "Pase rápido",
}
ZONE_LABELS = {
    "carnivore_zone": "Zona carnívora",
    "herbivore_zone": "Zona herbívora",
    "omnivore_zone": "Zona omnívora",
    "aquatic_zone": "Zona acuática",
    "aviary_zone": "Aviario",
}
CATEGORY_LABELS = {
    "food_carnivore": "Comida carnívora",
    "food_herbivore": "Comida herbívora",
    "food_omnivore": "Comida omnívora",
    "merchandise": "Mercancía",
    "beverage": "Bebidas",
    "medical": "Médico",
    "logistics": "Logística",
}
MAINTENANCE_LABELS = {
    "pending": "Pendiente",
    "in_progress": "En progreso",
    "completed": "Completada",
    "cancelled": "Cancelada",
}


class ReportsView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._svc = ReportService()
        self._hero_bg = None
        self._hero_logo_img = None
        self._build()

    def _build(self):
        topbar = ttk.Frame(self, style="Card.TFrame", padding=(18, 10))
        topbar.pack(fill="x", padx=28, pady=(16, 6))
        ttk.Label(topbar, text="Analítica / Panel ejecutivo", style="Muted.TLabel").pack(side="left")
        make_status_pill(topbar, "ANALÍTICA SQL ACTIVA").pack(side="right")

        hero_wrap = ttk.Frame(self, style="Card.TFrame", padding=(16, 12))
        hero_wrap.pack(fill="x", padx=28, pady=(0, 8))
        hero = tk.Canvas(hero_wrap, height=132, bg="#0B1412", highlightthickness=1, highlightbackground="#2B4A3F")
        hero.pack(fill="x")
        hero.bind("<Configure>", lambda e: self._render_hero(hero, e.width, e.height))

        tools = ttk.Frame(self, style="Card.TFrame", padding=(16, 10))
        tools.pack(fill="x", padx=28, pady=(0, 8))
        ttk.Label(tools, text="Acciones rápidas:", style="Subtitle.TLabel").pack(side="left")
        ttk.Button(tools, text="Exportar CSV", command=self._export_tickets_csv).pack(side="left", padx=8)
        ttk.Button(tools, text="Refrescar vista", command=self._refresh_view).pack(side="left", padx=8)

        self._build_exec_kpis()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        nb.add(self._tab_tickets(nb), text="🎟 Entradas")
        nb.add(self._tab_occupation(nb), text="📍 Ocupación")
        nb.add(self._tab_danger(nb), text="🦖 Peligro")
        nb.add(self._tab_low_stock(nb), text="📦 Existencias")
        nb.add(self._tab_maintenance(nb), text="🛠 Mantenimiento")
        nb.add(self._tab_employees(nb), text="👥 Empleados")

    def _refresh_view(self):
        for child in self.winfo_children():
            child.destroy()
        self._build()

    def _build_exec_kpis(self):
        kpi_wrap = ttk.Frame(self, style="Card.TFrame", padding=(16, 10))
        kpi_wrap.pack(fill="x", padx=28, pady=(0, 10))
        kpi_wrap.columnconfigure((0, 1, 2, 3), weight=1)

        revenue = self._svc.daily_revenue()
        tickets = self._svc.daily_tickets_count()
        low_stock = self._svc.low_stock_items()
        avg_danger_rows = self._svc.avg_danger_by_enclosure()
        danger_high = len([r for r in avg_danger_rows if (r["avg_danger"] or 0) >= 4])

        cards = [
            ("Ingresos hoy", f"€ {revenue:,.2f}", "#59F3BE"),
            ("Entradas vendidas", str(tickets), "#D9A441"),
            ("Existencias bajas", str(len(low_stock)), "#FF7D7A" if low_stock else "#59F3BE"),
            ("Recintos de alto riesgo", str(danger_high), "#7FE7F5"),
        ]
        for idx, (label, value, color) in enumerate(cards):
            tile = tk.Frame(kpi_wrap, bg="#0D1815", highlightthickness=1, highlightbackground="#2B4A3F")
            tile.grid(row=0, column=idx, sticky="nsew", padx=6, pady=4)
            tk.Label(tile, text=label, bg="#0D1815", fg="#87B6A2", font=("Segoe UI Variable", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
            tk.Label(tile, text=value, bg="#0D1815", fg=color, font=("Bahnschrift", 20, "bold")).pack(anchor="w", padx=12, pady=(0, 10))

    def _render_hero(self, canvas: tk.Canvas, width: int, height: int):
        if width < 120:
            return
        if not self._hero_logo_img:
            from views.ui_kit import load_brand_logo
            self._hero_logo_img = load_brand_logo(72, 72)
        canvas.delete("all")
        for x in range(0, width, 24):
            canvas.create_line(x, 0, x, height, fill="#17342C")
        for y in range(0, height, 20):
            canvas.create_line(0, y, width, y, fill="#153128")
        canvas.create_rectangle(16, 16, width - 16, height - 16, outline="#D9A441", width=1)
        canvas.create_rectangle(24, 24, width - 24, height - 24, outline="#2B4A3F", width=1)
        title_size = max(16, min(24, int(width * 0.021)))
        sub_size = max(9, min(12, int(width * 0.011)))
        canvas.create_text(36, 34, anchor="w", fill="#D9A441", font=("Bahnschrift", title_size, "bold"), text="Centro de Analítica Ejecutiva")
        canvas.create_text(
            36,
            68,
            anchor="w",
            fill="#E6F4EE",
            font=("Segoe UI Variable", sub_size, "bold"),
            text="Inteligencia de ingresos · Proyección de capacidad · Vigilancia de riesgos · Métricas de personal",
        )
        canvas.create_text(36, 92, anchor="w", fill="#2EF7B5", font=("Consolas", 10, "bold"), text="ESTADO: CANALES DE REPORTES EN LÍNEA")
        chip_x1 = width - 216
        chip_x2 = width - 32
        canvas.create_rectangle(chip_x1, 26, chip_x2, 52, fill="#0E1D19", outline="#D9A441")
        canvas.create_text((chip_x1 + chip_x2) // 2, 39, text="NÚCLEO ANALÍTICO", fill="#D9A441", font=("Consolas", 9, "bold"))
        if self._hero_logo_img:
            canvas.create_image(width - 92, height // 2 + 2, image=self._hero_logo_img)

    # ------------------------------------------------------------ helpers
    def _kpi(self, parent, label, value):
        f = ttk.Frame(parent, padding=(0, 8))
        f.pack(side="left", padx=(0, 18))
        lbl = ttk.Label(f, text=label, style="Muted.TLabel")
        lbl.pack(anchor="w")
        ttk.Label(f, text=value, style="Subtitle.TLabel").pack(anchor="w")

    def _table(self, parent, columns):
        wrap = ttk.Frame(parent, style="Card.TFrame", padding=(12, 10))
        wrap.pack(fill="both", expand=True, padx=12, pady=12)
        ttk.Label(wrap, text="REJILLA DE DATOS", style="Muted.TLabel").pack(anchor="w", pady=(0, 8))

        keys = [c[0] for c in columns]
        tv = ttk.Treeview(wrap, columns=keys, show="headings", height=12, style="Glow.Treeview")
        for k, t, w, anchor in columns:
            tv.heading(k, text=t)
            tv.column(k, width=w, anchor=anchor)

        tv.tag_configure("odd", background="#0D1815")
        tv.tag_configure("even", background="#0F1E1A")

        sb = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tv.pack(fill="both", expand=True)
        return tv

    def _bar_chart(self, parent, rows, label_key, value_key, title):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=(12, 10))
        frame.pack(fill="x", padx=12, pady=(8, 0))
        ttk.Label(frame, text=title, style="Subtitle.TLabel").pack(anchor="w", pady=(0, 8))
        canvas = tk.Canvas(frame, height=200, bg="#0B1412", highlightthickness=1, highlightbackground="#2B4A3F")
        canvas.pack(fill="x")
        def render(_event=None):
            canvas.delete("all")
            if not rows:
                canvas.create_text(20, 40, anchor="w", fill="#9fc9af", text="Sin datos para graficar.")
                return
            max_value = max(float(r[value_key]) for r in rows) or 1
            chart_w = max(420, canvas.winfo_width())
            left = 48
            top = 18
            bottom = 150
            right = chart_w - 24
            for gx in range(left, right, 44):
                canvas.create_line(gx, top, gx, bottom, fill="#132822")
            for gy in range(top, bottom + 1, 22):
                canvas.create_line(left, gy, right, gy, fill="#10211C")
            canvas.create_rectangle(left, top, right, bottom, outline="#2B4A3F")
            bar_area_w = right - left - 24
            count = max(1, len(rows))
            if count == 1:
                bar_w = int(bar_area_w * 0.6)
                gap = 0
                x = left + (bar_area_w - bar_w) // 2
            else:
                bar_w = max(24, int(bar_area_w / (count * 1.6)))
                gap = int(bar_w * 0.55)
                x = left + 18
            tooltip = {"rect": None, "text": None}
            bars: list[dict] = []
            spark_points: list[tuple[float, float]] = []
            for row in rows:
                val = float(row[value_key])
                label = str(row[label_key])
                bar_h = int((val / max_value) * (bottom - top - 10))
                y0 = bottom - bar_h
                canvas.create_rectangle(x, y0, x + bar_w, bottom, fill="#0E1D19", outline="#2EF7B5", width=1)
                canvas.create_rectangle(x, y0, x + bar_w, y0 + 5, fill="#7FE7F5", outline="")
                canvas.create_rectangle(x + 3, y0 + 6, x + bar_w - 3, bottom - 3, fill="#34B6C9", outline="")
                canvas.create_text(x + bar_w / 2, bottom + 18, fill="#E6F4EE", text=label[:10], font=("Segoe UI Variable", 9))
                canvas.create_text(x + bar_w / 2, y0 - 12, fill="#D9A441", text=f"{val:,.0f}", font=("Consolas", 9, "bold"))
                cx = x + bar_w / 2
                spark_points.append((cx, y0))
                bars.append({"bbox": (x, y0, x + bar_w, bottom), "label": label, "value": val})
                x += bar_w + gap
            if len(spark_points) >= 2:
                flat = [p for xy in spark_points for p in xy]
                canvas.create_line(*flat, fill="#D9A441", width=2, smooth=True)
                for cx, cy in spark_points:
                    canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="#D9A441", outline="")
            canvas.create_rectangle(left, bottom + 34, left + 14, bottom + 46, fill="#34B6C9", outline="")
            canvas.create_text(left + 22, bottom + 40, anchor="w", fill="#87B6A2", text="Serie principal", font=("Consolas", 9))

            def hide_tooltip():
                if tooltip["rect"] is not None:
                    canvas.delete(tooltip["rect"])
                    tooltip["rect"] = None
                if tooltip["text"] is not None:
                    canvas.delete(tooltip["text"])
                    tooltip["text"] = None

            def show_tooltip(xp: int, yp: int, label: str, val: float):
                hide_tooltip()
                msg = f"{label}: {val:,.2f}"
                tw = max(140, len(msg) * 7)
                x0 = min(max(left + 6, xp + 12), right - tw - 6)
                y0 = max(top + 6, yp - 34)
                tooltip["rect"] = canvas.create_rectangle(x0, y0, x0 + tw, y0 + 24, fill="#0E1D19", outline="#D9A441", width=1)
                tooltip["text"] = canvas.create_text(x0 + 10, y0 + 12, anchor="w", text=msg, fill="#E6F4EE", font=("Consolas", 9))

            def on_move(evt):
                for b in bars:
                    x1, y1, x2, y2 = b["bbox"]
                    if x1 <= evt.x <= x2 and y1 <= evt.y <= y2:
                        show_tooltip(evt.x, evt.y, str(b["label"]), float(b["value"]))
                        return
                hide_tooltip()

            canvas.bind("<Motion>", on_move)
            canvas.bind("<Leave>", lambda _e: hide_tooltip())
        canvas.bind("<Configure>", render)
        render()

    def _occupation_progress(self, parent, rows):
        """Barras de progreso estilo radar de capacidad."""
        card = ttk.Frame(parent, style="Card.TFrame", padding=(12, 10))
        card.pack(fill="x", padx=12, pady=(8, 0))
        ttk.Label(card, text="Capacidad por recinto (panel táctico)", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 8))

        c = tk.Canvas(card, height=220, bg="#0B1412", highlightthickness=1, highlightbackground="#2B4A3F")
        c.pack(fill="x")
        def render(_event=None):
            c.delete("all")
            w = max(460, c.winfo_width())
            h = max(220, int(c.cget("height")))
            for gx in range(20, w, 44):
                c.create_line(gx, 12, gx, h - 12, fill="#132822")
            for gy in range(12, h - 12, 22):
                c.create_line(20, gy, w - 20, gy, fill="#10211C")
            y = 24
            for row in rows[:6]:
                name = str(row["name"])
                occ = int(row["occupancy"])
                mx = int(row["max_capacity"]) if row["max_capacity"] else 1
                ratio = max(0.0, min(1.0, occ / mx))
                pct = ratio * 100
                c.create_text(28, y + 10, anchor="w", fill="#E6F4EE", font=("Segoe UI Variable", 10, "bold"), text=name[:26])
                stat_x = min(max(int(w * 0.32), 220), w - 250)
                c.create_text(stat_x, y + 10, anchor="w", fill="#87B6A2", font=("Consolas", 9), text=f"{occ}/{mx} ({pct:.0f}%)")
                track_x1 = min(max(int(w * 0.52), stat_x + 120), w - 180)
                track_x2 = w - 32
                c.create_rectangle(track_x1, y + 3, track_x2, y + 18, fill="#0E1D19", outline="#2B4A3F")
                fill_w = int((track_x2 - track_x1) * ratio)
                color = "#59F3BE" if pct < 70 else "#F4D27C" if pct < 90 else "#FF7D7A"
                c.create_rectangle(track_x1, y + 3, track_x1 + fill_w, y + 18, fill="#144438", outline=color, width=1)
                c.create_rectangle(track_x1, y + 3, track_x1 + min(fill_w, 18), y + 18, fill=color, outline="")
                y += 32
        c.bind("<Configure>", render)
        render()

    # ------------------------------------------------------------ tabs
    def _tab_tickets(self, parent):
        frame = ttk.Frame(parent)
        kpi_row = ttk.Frame(frame, padding=12)
        kpi_row.pack(fill="x")
        self._kpi(kpi_row, "Ingresos hoy", f"€ {self._svc.daily_revenue():,.2f}")
        self._kpi(kpi_row, "Entradas vendidas", str(self._svc.daily_tickets_count()))

        revenue_rows = self._svc.revenue_by_type()
        chart_rows = [
            {"ticket_type": TICKET_LABELS.get(r["ticket_type"], r["ticket_type"]), "revenue": r["revenue"]}
            for r in revenue_rows
        ]
        self._bar_chart(
            frame,
            chart_rows,
            label_key="ticket_type",
            value_key="revenue",
            title="Ingresos por tipo (visual táctico)",
        )

        tv = self._table(frame, [
            ("type", "Tipo", 200, "w"),
            ("qty",  "Cantidad", 120, "center"),
            ("rev",  "Ingreso (€)", 160, "e"),
        ])
        for r in revenue_rows:
            tv.insert("", "end", values=(
                TICKET_LABELS.get(r["ticket_type"], r["ticket_type"]), r["quantity"], f"{r['revenue']:.2f}"
            ), tags=("even" if (tv.get_children().__len__() % 2 == 0) else "odd",))
        return frame

    def _tab_occupation(self, parent):
        frame = ttk.Frame(parent)
        occ_rows = self._svc.occupation_by_zone()
        normalized = []
        for row in occ_rows:
            max_capacity = row["max_capacity"] or 1
            normalized.append(
                {
                    "name": row["name"],
                    "ratio": (row["occupancy"] / max_capacity) * 100,
                }
            )
        self._bar_chart(
            frame,
            normalized,
            label_key="name",
            value_key="ratio",
            title="Nivel de ocupación por recinto (%)",
        )
        self._occupation_progress(frame, occ_rows)

        tv = self._table(frame, [
            ("name",    "Recinto",     220, "w"),
            ("zone",    "Zona",        160, "w"),
            ("max",     "Máximo",      100, "center"),
            ("occ",     "Ocupación",   100, "center"),
            ("ratio",   "% Ocupación", 130, "center"),
        ])
        for r in occ_rows:
            ratio = (r["occupancy"] / r["max_capacity"] * 100
                     if r["max_capacity"] else 0)
            tv.insert("", "end", values=(
                r["name"], ZONE_LABELS.get(r["zone_type"], r["zone_type"]), r["max_capacity"],
                r["occupancy"], f"{ratio:.1f}%"
            ), tags=("even" if (tv.get_children().__len__() % 2 == 0) else "odd",))
        return frame

    def _tab_danger(self, parent):
        frame = ttk.Frame(parent)
        tv = self._table(frame, [
            ("name",  "Recinto",       240, "w"),
            ("avg",   "Peligro medio", 160, "center"),
            ("count", "Dinosaurios",   140, "center"),
        ])
        for r in self._svc.avg_danger_by_enclosure():
            tv.insert("", "end", values=(
                r["enclosure_name"],
                f"{r['avg_danger']:.2f}" if r["avg_danger"] is not None else "—",
                r["dinos"],
            ), tags=("even" if (tv.get_children().__len__() % 2 == 0) else "odd",))
        return frame

    def _tab_low_stock(self, parent):
        frame = ttk.Frame(parent)
        tv = self._table(frame, [
            ("name",     "Ítem",      220, "w"),
            ("category", "Categoría", 150, "w"),
            ("qty",      "Cantidad",  100, "center"),
            ("min",      "Mínimo",    100, "center"),
            ("supplier", "Proveedor", 180, "w"),
        ])
        for r in self._svc.low_stock_items():
            tv.insert("", "end", values=(
                r["item_name"], CATEGORY_LABELS.get(r["category"], r["category"]), r["quantity"],
                r["minimum_stock"], r["supplier"] or "—",
            ), tags=("even" if (tv.get_children().__len__() % 2 == 0) else "odd",))
        return frame

    def _tab_maintenance(self, parent):
        frame = ttk.Frame(parent)
        rows = self._svc.maintenance_by_status()
        chart_rows = [{"label": MAINTENANCE_LABELS.get(r["status"], r["status"]), "value": r["quantity"]} for r in rows]
        self._bar_chart(frame, chart_rows, "label", "value", "Distribución de mantenimiento")
        tv = self._table(frame, [
            ("status", "Estado",   200, "w"),
            ("qty",    "Cantidad", 140, "center"),
        ])
        for r in rows:
            tv.insert("", "end", values=(MAINTENANCE_LABELS.get(r["status"], r["status"]), r["quantity"]))
            tv.item(tv.get_children()[-1], tags=("even" if (tv.get_children().__len__() % 2 == 0) else "odd",))
        return frame

    def _tab_employees(self, parent):
        frame = ttk.Frame(parent)
        tv = self._table(frame, [
            ("role",   "Rol",            220, "w"),
            ("qty",    "Activos",        120, "center"),
            ("salary", "Salario medio",  160, "e"),
        ])
        for r in self._svc.employees_by_role():
            tv.insert("", "end", values=(
                r["role"], r["quantity"], f"€ {r['avg_salary']:,.2f}"
            ), tags=("even" if (tv.get_children().__len__() % 2 == 0) else "odd",))
        return frame

    def _export_tickets_csv(self):
        rows = self._svc.revenue_by_type()
        if not rows:
            return
        target = filedialog.asksaveasfilename(
            title="Guardar reporte de entradas",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not target:
            return
        with open(target, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["tipo_entrada", "cantidad", "ingresos"])
            for r in rows:
                writer.writerow([TICKET_LABELS.get(r["ticket_type"], r["ticket_type"]), r["quantity"], r["revenue"]])
