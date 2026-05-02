"""Vista CRUD de Recintos."""
import tkinter as tk
from tkinter import messagebox, ttk

from services.enclosure_service import EnclosureService
from utils.constants import ENCLOSURE_STATUSES
from utils.exceptions import DinoReserveError
from utils.validators import tk_validate_float, tk_validate_int
from views.crud_helpers import FormDialog, make_section_header, make_toolbar, make_treeview
from views.ui_kit import draw_kpi_tile
from views.ui_kit import StatusPill

ZONE_TYPES = ("carnivore_zone", "herbivore_zone", "omnivore_zone",
              "aquatic_zone", "aviary_zone")
ZONE_LABELS = {
    "carnivore_zone": "Zona carnívora",
    "herbivore_zone": "Zona herbívora",
    "omnivore_zone": "Zona omnívora",
    "aquatic_zone": "Zona acuática",
    "aviary_zone": "Aviario",
}
ZONE_VALUES = {label: value for value, label in ZONE_LABELS.items()}
STATUS_LABELS = {"active": "Activo", "maintenance": "Mantenimiento", "closed": "Cerrado"}
STATUS_VALUES = {label: value for value, label in STATUS_LABELS.items()}
ALL_LABEL = "Todos"


class EnclosureView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._svc = EnclosureService()
        self._q_var = tk.StringVar()
        self._status_filter = tk.StringVar(value=ALL_LABEL)
        self._build()

    def _build(self):
        make_section_header(
            self, "Recintos del parque",
            "Capacidad, voltaje de vallas y nivel de seguridad.",
            module_key="security",
        )
        bar = make_toolbar(self)
        ttk.Entry(bar, textvariable=self._q_var, width=28).pack(side="left", padx=(0, 8))
        ttk.Combobox(bar, textvariable=self._status_filter, state="readonly",
                     values=[ALL_LABEL, *STATUS_LABELS.values()], width=14).pack(side="left", padx=(0, 10))
        ttk.Button(bar, text="Filtrar", command=self._refresh).pack(side="left", padx=(0, 12))
        ttk.Button(bar, text="➕  Nuevo", style="Accent.TButton",
                   command=self._on_new).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✏  Editar", command=self._on_edit).pack(side="left", padx=6)
        ttk.Button(bar, text="🗑  Eliminar", style="Danger.TButton",
                   command=self._on_delete).pack(side="left", padx=6)
        ttk.Button(bar, text="🔄  Refrescar",
                   command=self._refresh).pack(side="right")

        all_enc = self._svc.list_all()
        active = len([e for e in all_enc if e.status == "active"])
        maint = len([e for e in all_enc if e.status == "maintenance"])
        stats = ttk.Frame(self, style="Card.TFrame", padding=(14, 10))
        stats.pack(fill="x", padx=12, pady=(0, 10))
        for i, (label, value, color) in enumerate([
            ("Recintos totales", str(len(all_enc)), "#D9534F"),
            ("Activos", str(active), "#FF7D7A"),
            ("Mantenimiento", str(maint), "#F7B2AF"),
        ]):
            stats.columnconfigure(i, weight=1)
            draw_kpi_tile(stats, label, value, color).grid(row=0, column=i, sticky="nsew", padx=6)

        self._tree = make_treeview(self, [
            ("id",        "ID",        50,  "center"),
            ("name",      "Nombre",    220, "w"),
            ("zone",      "Zona",      150, "w"),
            ("cur",       "Actual",    80,  "center"),
            ("max",       "Máximo",    80,  "center"),
            ("voltage",   "Voltaje",   100, "center"),
            ("security",  "Seguridad", 100, "center"),
            ("status",    "Estado",    140, "center"),
        ])
        self._tree.tag_configure("active", foreground="#59F3BE")
        self._tree.tag_configure("maintenance", foreground="#FFB366")
        self._tree.tag_configure("closed", foreground="#FF7D7A")
        self._tree.bind("<Double-1>", lambda _e: self._on_edit())
        self._tree.bind("<<TreeviewSelect>>", lambda _e: self._render_detail())

        self._detail = ttk.Frame(self, style="Card.TFrame", padding=(16, 12))
        self._detail.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Label(self._detail, text="Detalle seleccionado", style="Subtitle.TLabel").pack(anchor="w")
        row = ttk.Frame(self._detail, style="Card.TFrame")
        row.pack(anchor="w", pady=(8, 0))
        self._pill_status = StatusPill(row, "ESTADO: —", accent="#FF7D7A")
        self._pill_status.pack(side="left", padx=(0, 10))
        self._pill_security = StatusPill(row, "SEGURIDAD: —", accent="#D9A441")
        self._pill_security.pack(side="left")
        self._detail_text = ttk.Label(self._detail, text="Selecciona un recinto para ver detalle.", style="Muted.TLabel")
        self._detail_text.pack(anchor="w", pady=(8, 0))
        self._refresh()

    def _refresh(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        query = self._q_var.get().strip().lower()
        status = STATUS_VALUES.get(self._status_filter.get())
        for e in self._svc.list_all():
            if query and query not in f"{e.name} {ZONE_LABELS.get(e.zone_type, e.zone_type)}".lower():
                continue
            if status and e.status != status:
                continue
            self._tree.insert(
                "", "end", iid=str(e.id),
                values=(e.id, e.name, ZONE_LABELS.get(e.zone_type, e.zone_type), e.current_capacity,
                        e.max_capacity, f"{e.fence_voltage:.0f}V",
                        f"Nivel {e.security_level}", STATUS_LABELS.get(e.status, e.status)),
                tags=(e.status,),
            )
        self._render_detail()

    def _render_detail(self):
        sel = self._tree.selection()
        if not sel:
            self._pill_status.set("ESTADO: —", accent="#FF7D7A")
            self._pill_security.set("SEGURIDAD: —", accent="#D9A441")
            self._detail_text.configure(text="Selecciona un recinto para ver detalle.")
            return
        vals = self._tree.item(sel[0]).get("values", [])
        # id, name, zone, cur, max, voltage, security, status
        try:
            name = vals[1]
            cur = int(vals[3])
            mx = int(vals[4])
            voltage = vals[5]
            sec = str(vals[6]).upper()
            status = STATUS_VALUES.get(str(vals[7]), str(vals[7])).upper()
        except Exception:
            return
        accent = {"ACTIVE": "#59F3BE", "MAINTENANCE": "#FFB366", "CLOSED": "#FF7D7A"}.get(status, "#59F3BE")
        estado_es = {"ACTIVE": "ACTIVO", "MAINTENANCE": "MANTENIMIENTO", "CLOSED": "CERRADO"}.get(status, status)
        self._pill_status.set(f"ESTADO: {estado_es}", accent=accent)
        self._pill_security.set(sec.replace("NIVEL", "NIVEL"), accent="#D9A441")
        pct = (cur / mx * 100) if mx else 0
        self._detail_text.configure(text=f"{name} · Capacidad: {cur}/{mx} ({pct:.0f}%) · Valla: {voltage}")

    def _form_fields(self):
        return [
            ("name",            "Nombre", "entry", None),
            ("zone_type",       "Tipo de zona", "combo",
             {"values": list(ZONE_LABELS.values()), "default": ZONE_LABELS[ZONE_TYPES[0]]}),
            ("max_capacity",    "Capacidad máxima", "spin",
             {"from_": 1, "to": 100, "default": 5, "validate": tk_validate_int}),
            ("current_capacity","Capacidad actual", "spin",
             {"from_": 0, "to": 100, "default": 0, "validate": tk_validate_int}),
            ("fence_voltage",   "Voltaje de valla (V)", "entry",
             {"validate": tk_validate_float, "default": 5000}),
            ("security_level",  "Nivel de seguridad (1-5)", "spin",
             {"from_": 1, "to": 5, "default": 3, "validate": tk_validate_int}),
            ("status",          "Estado", "combo",
             {"values": list(STATUS_LABELS.values()), "default": STATUS_LABELS["active"]}),
        ]

    def _selected(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un recinto.", parent=self)
            return None
        return int(sel[0])

    def _on_new(self):
        dlg = FormDialog(self.winfo_toplevel(), "Nuevo recinto", self._form_fields())
        self.wait_window(dlg)
        if not dlg.result:
            return
        try:
            data = dict(dlg.result)
            data["zone_type"] = ZONE_VALUES.get(data["zone_type"], data["zone_type"])
            data["status"] = STATUS_VALUES.get(data["status"], data["status"])
            self._svc.create(data)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _on_edit(self):
        eid = self._selected()
        if eid is None:
            return
        from repositories.enclosure_repository import EnclosureRepository
        enc = EnclosureRepository().get(eid)
        if enc is None:
            return
        initial = enc.to_dict()
        initial["zone_type"] = ZONE_LABELS.get(initial["zone_type"], initial["zone_type"])
        initial["status"] = STATUS_LABELS.get(initial["status"], initial["status"])
        dlg = FormDialog(self.winfo_toplevel(), f"Editar {enc.name}",
                         self._form_fields(), initial=initial)
        self.wait_window(dlg)
        if not dlg.result:
            return
        try:
            data = dict(dlg.result)
            data["zone_type"] = ZONE_VALUES.get(data["zone_type"], data["zone_type"])
            data["status"] = STATUS_VALUES.get(data["status"], data["status"])
            self._svc.update(eid, data)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _on_delete(self):
        eid = self._selected()
        if eid is None:
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar recinto #{eid}?", parent=self):
            return
        try:
            self._svc.delete(eid)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)
