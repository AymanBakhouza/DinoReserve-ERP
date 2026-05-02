"""Vista CRUD de Mantenimiento."""
import tkinter as tk
from tkinter import messagebox, ttk

from repositories.employee_repository import EmployeeRepository
from services.maintenance_service import MaintenanceService
from utils.constants import MAINTENANCE_PRIORITIES, MAINTENANCE_STATUSES
from utils.exceptions import DinoReserveError
from views.crud_helpers import FormDialog, make_section_header, make_toolbar, make_treeview
from views.ui_kit import draw_kpi_tile
from views.ui_kit import StatusPill

ASSET_TYPES = ("fence", "enclosure", "vehicle", "attraction", "power", "other")
ASSET_LABELS = {
    "fence": "Valla",
    "enclosure": "Recinto",
    "vehicle": "Vehículo",
    "attraction": "Atracción",
    "power": "Energía",
    "other": "Otro",
}
ASSET_VALUES = {label: value for value, label in ASSET_LABELS.items()}
STATUS_LABELS = {
    "pending": "Pendiente",
    "in_progress": "En progreso",
    "completed": "Completada",
    "cancelled": "Cancelada",
}
STATUS_VALUES = {label: value for value, label in STATUS_LABELS.items()}
PRIORITY_LABELS = {"low": "Baja", "medium": "Media", "high": "Alta", "critical": "Crítica"}
PRIORITY_VALUES = {label: value for value, label in PRIORITY_LABELS.items()}
ALL_LABEL = "Todos"


class MaintenanceView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._svc = MaintenanceService()
        self._emp_repo = EmployeeRepository()
        self._q_var = tk.StringVar()
        self._status_filter = tk.StringVar(value=ALL_LABEL)
        self._priority_filter = tk.StringVar(value=ALL_LABEL)
        self._build()

    def _build(self):
        make_section_header(
            self, "Mantenimiento del parque",
            "Tareas de revisión y reparación con prioridad y asignación.",
            module_key="maintenance",
        )
        bar = make_toolbar(self)
        ttk.Entry(bar, textvariable=self._q_var, width=24).pack(side="left", padx=(0, 8))
        ttk.Combobox(bar, textvariable=self._status_filter, state="readonly",
                     values=[ALL_LABEL, *STATUS_LABELS.values()], width=14).pack(side="left", padx=(0, 8))
        ttk.Combobox(bar, textvariable=self._priority_filter, state="readonly",
                     values=[ALL_LABEL, *PRIORITY_LABELS.values()], width=12).pack(side="left", padx=(0, 10))
        ttk.Button(bar, text="Filtrar", command=self._refresh).pack(side="left", padx=(0, 12))
        ttk.Button(bar, text="➕  Nueva tarea", style="Accent.TButton",
                   command=self._on_new).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✏  Editar", command=self._on_edit).pack(side="left", padx=6)
        ttk.Button(bar, text="🗑  Eliminar", style="Danger.TButton",
                   command=self._on_delete).pack(side="left", padx=6)
        ttk.Button(bar, text="🔄  Refrescar",
                   command=self._refresh).pack(side="right")

        tasks = self._svc.list_all()
        critical = len([t for t in tasks if t.priority == "critical"])
        in_progress = len([t for t in tasks if t.status == "in_progress"])
        stats = ttk.Frame(self, style="Card.TFrame", padding=(14, 10))
        stats.pack(fill="x", padx=12, pady=(0, 10))
        for i, (label, value, color) in enumerate([
            ("Tareas", str(len(tasks)), "#C85050"),
            ("En progreso", str(in_progress), "#FF8A8A"),
            ("Críticas", str(critical), "#FF5D5D"),
        ]):
            stats.columnconfigure(i, weight=1)
            draw_kpi_tile(stats, label, value, color).grid(row=0, column=i, sticky="nsew", padx=6)

        self._tree = make_treeview(self, [
            ("id",         "ID",         50,  "center"),
            ("asset",      "Activo",     220, "w"),
            ("type",       "Tipo",       110, "center"),
            ("priority",   "Prioridad",  100, "center"),
            ("employee",   "Asignado a", 200, "w"),
            ("status",     "Estado",     130, "center"),
            ("created",    "Creada",     150, "center"),
        ])
        self._tree.tag_configure("critical", foreground="#FF7D7A")
        self._tree.tag_configure("high", foreground="#FFB366")
        self._tree.tag_configure("medium", foreground="#F4D27C")
        self._tree.tag_configure("low", foreground="#7FE7F5")
        self._tree.bind("<Double-1>", lambda _e: self._on_edit())
        self._tree.bind("<<TreeviewSelect>>", lambda _e: self._render_detail())

        self._detail = ttk.Frame(self, style="Card.TFrame", padding=(16, 12))
        self._detail.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Label(self._detail, text="Detalle seleccionado", style="Subtitle.TLabel").pack(anchor="w")
        row = ttk.Frame(self._detail, style="Card.TFrame")
        row.pack(anchor="w", pady=(8, 0))
        self._pill_priority = StatusPill(row, "PRIORIDAD: —", accent="#FF7D7A")
        self._pill_priority.pack(side="left", padx=(0, 10))
        self._pill_status = StatusPill(row, "ESTADO: —", accent="#7FE7F5")
        self._pill_status.pack(side="left")
        self._detail_text = ttk.Label(self._detail, text="Selecciona una tarea para ver detalle.", style="Muted.TLabel")
        self._detail_text.pack(anchor="w", pady=(8, 0))
        self._refresh()

    def _employee_choices(self):
        choices = [("0 — Sin asignar", None)]
        for e in self._emp_repo.list_all():
            choices.append((f"{e.id} — {e.name}", e.id))
        return choices

    def _resolve(self, label, choices):
        for lbl, eid in choices:
            if lbl == label:
                return eid
        return None

    def _refresh(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        emp_map = {e.id: e.name for e in self._emp_repo.list_all()}
        query = self._q_var.get().strip().lower()
        status = STATUS_VALUES.get(self._status_filter.get())
        priority = PRIORITY_VALUES.get(self._priority_filter.get())
        for t in self._svc.list_all():
            if query and query not in f"{t.asset_name} {ASSET_LABELS.get(t.asset_type, t.asset_type)}".lower():
                continue
            if status and t.status != status:
                continue
            if priority and t.priority != priority:
                continue
            self._tree.insert(
                "", "end", iid=str(t.id),
                values=(t.id, t.asset_name, ASSET_LABELS.get(t.asset_type, t.asset_type),
                        PRIORITY_LABELS.get(t.priority, t.priority),
                        emp_map.get(t.assigned_employee_id, "Sin asignar")
                        if t.assigned_employee_id else "Sin asignar",
                        STATUS_LABELS.get(t.status, t.status), t.created_at),
                tags=(t.priority,),
            )
        self._render_detail()

    def _render_detail(self):
        sel = self._tree.selection()
        if not sel:
            self._pill_priority.set("PRIORIDAD: —", accent="#FF7D7A")
            self._pill_status.set("ESTADO: —", accent="#7FE7F5")
            self._detail_text.configure(text="Selecciona una tarea para ver detalle.")
            return
        vals = self._tree.item(sel[0]).get("values", [])
        # id, asset, type, priority, employee, status, created
        try:
            asset = vals[1]
            priority = PRIORITY_VALUES.get(str(vals[3]), str(vals[3])).upper()
            status = STATUS_VALUES.get(str(vals[5]), str(vals[5])).upper()
            employee = vals[4]
        except Exception:
            return
        p_color = {"CRITICAL": "#FF7D7A", "HIGH": "#FFB366", "MEDIUM": "#F4D27C", "LOW": "#7FE7F5"}.get(priority, "#F4D27C")
        pri_es = {"CRITICAL": "CRÍTICA", "HIGH": "ALTA", "MEDIUM": "MEDIA", "LOW": "BAJA"}.get(priority, priority)
        st_es = {"PENDING": "PENDIENTE", "IN_PROGRESS": "EN PROGRESO", "COMPLETED": "COMPLETADA"}.get(status, status)
        self._pill_priority.set(f"PRIORIDAD: {pri_es}", accent=p_color)
        self._pill_status.set(f"ESTADO: {st_es[:12]}", accent="#7FE7F5")
        self._detail_text.configure(text=f"{asset} · Asignado a: {employee}")

    def _form_fields(self):
        choices = self._employee_choices()
        labels = [c[0] for c in choices]
        return choices, [
            ("asset_name", "Nombre del activo", "entry", None),
            ("asset_type", "Tipo", "combo",
             {"values": list(ASSET_LABELS.values()), "default": ASSET_LABELS["fence"]}),
            ("priority",   "Prioridad", "combo",
             {"values": list(PRIORITY_LABELS.values()), "default": PRIORITY_LABELS["medium"]}),
            ("emp_label",  "Asignar empleado", "combo",
             {"values": labels, "default": labels[0]}),
            ("status",     "Estado", "combo",
             {"values": list(STATUS_LABELS.values()), "default": STATUS_LABELS["pending"]}),
            ("description","Descripción", "text", {"default": ""}),
        ]

    def _selected(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona una tarea.", parent=self)
            return None
        return int(sel[0])

    def _on_new(self):
        choices, fields = self._form_fields()
        dlg = FormDialog(self.winfo_toplevel(), "Nueva tarea de mantenimiento", fields)
        self.wait_window(dlg)
        if not dlg.result:
            return
        data = dict(dlg.result)
        data["asset_type"] = ASSET_VALUES.get(data["asset_type"], data["asset_type"])
        data["priority"] = PRIORITY_VALUES.get(data["priority"], data["priority"])
        data["status"] = STATUS_VALUES.get(data["status"], data["status"])
        data["assigned_employee_id"] = self._resolve(data.pop("emp_label"), choices)
        try:
            self._svc.create(data)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _on_edit(self):
        task_id = self._selected()
        if task_id is None:
            return
        from repositories.maintenance_repository import MaintenanceRepository
        task = MaintenanceRepository().get(task_id)
        if task is None:
            return
        choices, fields = self._form_fields()
        labels = [c[0] for c in choices]
        sel_label = labels[0]
        for lbl, eid in choices:
            if eid == task.assigned_employee_id:
                sel_label = lbl
                break
        initial = task.to_dict()
        initial["asset_type"] = ASSET_LABELS.get(initial["asset_type"], initial["asset_type"])
        initial["priority"] = PRIORITY_LABELS.get(initial["priority"], initial["priority"])
        initial["status"] = STATUS_LABELS.get(initial["status"], initial["status"])
        initial["emp_label"] = sel_label
        dlg = FormDialog(self.winfo_toplevel(), f"Editar tarea #{task_id}",
                         fields, initial=initial)
        self.wait_window(dlg)
        if not dlg.result:
            return
        data = dict(dlg.result)
        data["asset_type"] = ASSET_VALUES.get(data["asset_type"], data["asset_type"])
        data["priority"] = PRIORITY_VALUES.get(data["priority"], data["priority"])
        data["status"] = STATUS_VALUES.get(data["status"], data["status"])
        data["assigned_employee_id"] = self._resolve(data.pop("emp_label"), choices)
        try:
            self._svc.update(task_id, data)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _on_delete(self):
        task_id = self._selected()
        if task_id is None:
            return
        if not messagebox.askyesno(
            "Confirmar", f"¿Eliminar tarea #{task_id}?", parent=self
        ):
            return
        try:
            self._svc.delete(task_id)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)
