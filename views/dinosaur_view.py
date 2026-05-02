"""Vista CRUD de Dinosaurios."""
import tkinter as tk
from tkinter import messagebox, ttk

from repositories.enclosure_repository import EnclosureRepository
from services.dinosaur_service import DinosaurService
from utils.constants import DIET_TYPES, HEALTH_STATUSES
from utils.exceptions import DinoReserveError
from utils.validators import tk_validate_int
from views.crud_helpers import FormDialog, make_section_header, make_toolbar, make_treeview
from views.ui_kit import draw_kpi_tile
from views.ui_kit import StatusPill

DIET_LABELS = {
    "carnivore": "Carnívoro",
    "herbivore": "Herbívoro",
    "omnivore": "Omnívoro",
}
HEALTH_LABELS = {
    "healthy": "Sano",
    "observation": "Observación",
    "sick": "Enfermo",
    "critical": "Crítico",
}
DIET_VALUES = {label: value for value, label in DIET_LABELS.items()}
HEALTH_VALUES = {label: value for value, label in HEALTH_LABELS.items()}
ALL_LABEL = "Todos"


class DinosaurView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._svc = DinosaurService()
        self._enc_repo = EnclosureRepository()
        self._q_var = tk.StringVar()
        self._diet_filter = tk.StringVar(value=ALL_LABEL)
        self._health_filter = tk.StringVar(value=ALL_LABEL)
        self._build()

    def _build(self):
        make_section_header(
            self, "Gestión de dinosaurios",
            "Alta, baja y modificación de ejemplares en los recintos.",
            module_key="dinosaurs",
        )

        bar = make_toolbar(self)
        ttk.Entry(bar, textvariable=self._q_var, width=28).pack(side="left", padx=(0, 8))
        ttk.Combobox(
            bar,
            textvariable=self._diet_filter,
            state="readonly",
            values=[ALL_LABEL, *DIET_LABELS.values()],
            width=12,
        ).pack(side="left", padx=(0, 8))
        ttk.Combobox(
            bar,
            textvariable=self._health_filter,
            state="readonly",
            values=[ALL_LABEL, *HEALTH_LABELS.values()],
            width=14,
        ).pack(side="left", padx=(0, 10))
        ttk.Button(bar, text="Buscar", command=self._refresh).pack(side="left", padx=(0, 12))
        ttk.Button(bar, text="➕  Nuevo", style="Accent.TButton",
                   command=self._on_new).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✏  Editar", command=self._on_edit).pack(side="left", padx=6)
        ttk.Button(bar, text="🗑  Eliminar", style="Danger.TButton",
                   command=self._on_delete).pack(side="left", padx=6)
        ttk.Button(bar, text="🔄  Refrescar",
                   command=self._refresh).pack(side="right")

        stats = ttk.Frame(self, style="Card.TFrame", padding=(14, 10))
        stats.pack(fill="x", padx=12, pady=(0, 10))
        total = len(self._svc.list_all())
        carn = len([d for d in self._svc.list_all() if d.diet_type == "carnivore"])
        critical = len([d for d in self._svc.list_all() if d.health_status == "critical"])
        for i, (label, value, color) in enumerate([
            ("Ejemplares", str(total), "#1EB980"),
            ("Carnívoros", str(carn), "#59F3BE"),
            ("Salud crítica", str(critical), "#FF7D7A"),
        ]):
            stats.columnconfigure(i, weight=1)
            draw_kpi_tile(stats, label, value, color).grid(row=0, column=i, sticky="nsew", padx=6)

        self._tree = make_treeview(self, [
            ("id",            "ID",          50,  "center"),
            ("name",          "Nombre",      150, "w"),
            ("species",       "Especie",     180, "w"),
            ("diet_type",     "Dieta",       110, "center"),
            ("danger_level",  "Peligro",     90,  "center"),
            ("health_status", "Salud",       130, "center"),
            ("enclosure",     "Recinto",     180, "w"),
            ("feeding_level", "Alimentación",110, "center"),
            ("risk",          "Riesgo calc.",110, "center"),
        ])
        self._tree.tag_configure("healthy", foreground="#59F3BE")
        self._tree.tag_configure("observation", foreground="#F4D27C")
        self._tree.tag_configure("sick", foreground="#FFB366")
        self._tree.tag_configure("critical", foreground="#FF7D7A")
        self._tree.bind("<Double-1>", lambda _e: self._on_edit())
        self._tree.bind("<<TreeviewSelect>>", lambda _e: self._render_detail())

        self._detail = ttk.Frame(self, style="Card.TFrame", padding=(16, 12))
        self._detail.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Label(self._detail, text="Detalle seleccionado", style="Subtitle.TLabel").pack(anchor="w")
        self._pill_row = ttk.Frame(self._detail, style="Card.TFrame")
        self._pill_row.pack(anchor="w", pady=(8, 0))
        self._pill_health = StatusPill(self._pill_row, "SALUD: —", accent="#59F3BE")
        self._pill_health.pack(side="left", padx=(0, 10))
        self._pill_risk = StatusPill(self._pill_row, "RIESGO: —", accent="#D9A441")
        self._pill_risk.pack(side="left")

        self._detail_text = ttk.Label(self._detail, text="Selecciona un dinosaurio para ver detalles.", style="Muted.TLabel")
        self._detail_text.pack(anchor="w", pady=(8, 0))
        self._refresh()

    # ------------------------------------------------------------
    def _enclosure_choices(self):
        encs = self._enc_repo.list_all()
        # primer opción = sin recinto
        choices = [("0 — Sin asignar", None)]
        for e in encs:
            choices.append((f"{e.id} — {e.name}", e.id))
        return choices

    def _refresh(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        enc_map = {e.id: e.name for e in self._enc_repo.list_all()}
        query = self._q_var.get().strip().lower()
        diet = DIET_VALUES.get(self._diet_filter.get())
        health = HEALTH_VALUES.get(self._health_filter.get())
        for d in self._svc.list_all():
            if query and query not in f"{d.name} {d.species}".lower():
                continue
            if diet and d.diet_type != diet:
                continue
            if health and d.health_status != health:
                continue
            self._tree.insert(
                "", "end", iid=str(d.id),
                values=(d.id, d.name, d.species,
                        DIET_LABELS.get(d.diet_type, d.diet_type), d.danger_level,
                        HEALTH_LABELS.get(d.health_status, d.health_status),
                        enc_map.get(d.enclosure_id, "Sin asignar")
                        if d.enclosure_id else "Sin asignar",
                        d.feeding_level, d.calculate_risk_level()),
                tags=(d.health_status,),
            )
        self._render_detail()

    def _render_detail(self):
        sel = self._tree.selection()
        if not sel:
            self._pill_health.set("SALUD: —", accent="#59F3BE")
            self._pill_risk.set("RIESGO: —", accent="#D9A441")
            self._detail_text.configure(text="Selecciona un dinosaurio para ver detalles.")
            return
        item = self._tree.item(sel[0])
        vals = item.get("values", [])
        # columns: id, name, species, diet, danger, health, enclosure, feeding, risk
        try:
            name = vals[1]
            species = vals[2]
            health = HEALTH_VALUES.get(str(vals[5]), str(vals[5])).upper()
            feeding = vals[7]
            risk = vals[8]
        except Exception:
            return
        accent = {"HEALTHY": "#59F3BE", "OBSERVATION": "#F4D27C", "SICK": "#FFB366", "CRITICAL": "#FF7D7A"}.get(health, "#59F3BE")
        health_es = {"HEALTHY": "SANO", "OBSERVATION": "OBSERVACIÓN", "SICK": "ENFERMO", "CRITICAL": "CRÍTICO"}.get(health, health)
        self._pill_health.set(f"SALUD: {str(vals[5]).upper()}", accent=accent)
        self._pill_risk.set(f"RIESGO: {risk}", accent="#D9A441" if int(risk) < 7 else "#FFB366")
        self._detail_text.configure(text=f"{name} · {species} · Alimentación: {feeding}%")

    # ------------------------------------------------------------
    def _form_fields(self):
        choices = self._enclosure_choices()
        labels = [c[0] for c in choices]
        return labels, choices, [
            ("name",          "Nombre",         "entry", None),
            ("species",       "Especie",        "entry", None),
            ("diet_type",     "Dieta",          "combo",
             {"values": list(DIET_LABELS.values()), "default": DIET_LABELS["carnivore"]}),
            ("danger_level",  "Nivel de peligro (1-5)", "spin",
             {"from_": 1, "to": 5, "default": 1, "validate": tk_validate_int}),
            ("health_status", "Salud",          "combo",
             {"values": list(HEALTH_LABELS.values()), "default": HEALTH_LABELS["healthy"]}),
            ("feeding_level", "Alimentación (0-100)", "spin",
             {"from_": 0, "to": 100, "default": 100, "validate": tk_validate_int}),
            ("enclosure_label", "Recinto", "combo",
             {"values": labels, "default": labels[0] if labels else ""}),
        ]

    def _resolve_enclosure(self, label, choices):
        for lbl, eid in choices:
            if lbl == label:
                return eid
        return None

    def _selected(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un dinosaurio.", parent=self)
            return None
        return int(sel[0])

    # ------------------------------------------------------------
    def _on_new(self):
        labels, choices, fields = self._form_fields()
        dlg = FormDialog(self.winfo_toplevel(), "Nuevo dinosaurio", fields)
        self.wait_window(dlg)
        if not dlg.result:
            return
        data = dict(dlg.result)
        data["diet_type"] = DIET_VALUES.get(data["diet_type"], data["diet_type"])
        data["health_status"] = HEALTH_VALUES.get(data["health_status"], data["health_status"])
        data["enclosure_id"] = self._resolve_enclosure(data.pop("enclosure_label"), choices)
        try:
            self._svc.create(data)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _on_edit(self):
        dino_id = self._selected()
        if dino_id is None:
            return
        labels, choices, fields = self._form_fields()
        from repositories.dinosaur_repository import DinosaurRepository
        dino = DinosaurRepository().get(dino_id)
        if dino is None:
            return
        # determinar el label del recinto seleccionado
        sel_label = labels[0]
        for lbl, eid in choices:
            if eid == dino.enclosure_id:
                sel_label = lbl
                break
        initial = dino.to_dict()
        initial["diet_type"] = DIET_LABELS.get(initial["diet_type"], initial["diet_type"])
        initial["health_status"] = HEALTH_LABELS.get(initial["health_status"], initial["health_status"])
        initial["enclosure_label"] = sel_label
        dlg = FormDialog(self.winfo_toplevel(), f"Editar {dino.name}",
                         fields, initial=initial)
        self.wait_window(dlg)
        if not dlg.result:
            return
        data = dict(dlg.result)
        data["diet_type"] = DIET_VALUES.get(data["diet_type"], data["diet_type"])
        data["health_status"] = HEALTH_VALUES.get(data["health_status"], data["health_status"])
        data["enclosure_id"] = self._resolve_enclosure(data.pop("enclosure_label"), choices)
        try:
            self._svc.update(dino_id, data)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _on_delete(self):
        dino_id = self._selected()
        if dino_id is None:
            return
        if not messagebox.askyesno(
            "Confirmar", f"¿Eliminar dinosaurio #{dino_id}?", parent=self
        ):
            return
        try:
            self._svc.delete(dino_id)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)
