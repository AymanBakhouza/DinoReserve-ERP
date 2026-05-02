"""Vista CRUD de Empleados."""
import tkinter as tk
from tkinter import messagebox, ttk

from repositories.enclosure_repository import EnclosureRepository
from services.employee_service import EmployeeService
from utils.constants import EMPLOYEE_ROLES, EMPLOYEE_STATUSES
from utils.exceptions import DinoReserveError
from utils.validators import tk_validate_float, tk_validate_int
from views.crud_helpers import FormDialog, make_section_header, make_toolbar, make_treeview
from views.ui_kit import draw_kpi_tile
from views.ui_kit import StatusPill

STATUS_LABELS = {"active": "Activo", "inactive": "Inactivo", "vacation": "Vacaciones"}
STATUS_VALUES = {label: value for value, label in STATUS_LABELS.items()}
ALL_LABEL = "Todos"


class EmployeeView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._svc = EmployeeService()
        self._enc_repo = EnclosureRepository()
        self._q_var = tk.StringVar()
        self._role_filter = tk.StringVar(value=ALL_LABEL)
        self._status_filter = tk.StringVar(value=ALL_LABEL)
        self._build()

    def _build(self):
        make_section_header(
            self, "Equipo del parque",
            "Plantilla operativa: roles, salarios y zonas asignadas.",
            module_key="hr",
        )
        bar = make_toolbar(self)
        ttk.Entry(bar, textvariable=self._q_var, width=24).pack(side="left", padx=(0, 8))
        ttk.Combobox(bar, textvariable=self._role_filter, state="readonly",
                     values=[ALL_LABEL, *EMPLOYEE_ROLES], width=20).pack(side="left", padx=(0, 8))
        ttk.Combobox(bar, textvariable=self._status_filter, state="readonly",
                     values=[ALL_LABEL, *STATUS_LABELS.values()], width=12).pack(side="left", padx=(0, 10))
        ttk.Button(bar, text="Filtrar", command=self._refresh).pack(side="left", padx=(0, 12))
        ttk.Button(bar, text="➕  Nuevo", style="Accent.TButton",
                   command=self._on_new).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✏  Editar", command=self._on_edit).pack(side="left", padx=6)
        ttk.Button(bar, text="🗑  Eliminar", style="Danger.TButton",
                   command=self._on_delete).pack(side="left", padx=6)
        ttk.Button(bar, text="🔄  Refrescar",
                   command=self._refresh).pack(side="right")

        emps = self._svc.list_all()
        active = len([e for e in emps if e.status == "active"])
        avg_salary = (sum(e.salary for e in emps) / len(emps)) if emps else 0
        stats = ttk.Frame(self, style="Card.TFrame", padding=(14, 10))
        stats.pack(fill="x", padx=12, pady=(0, 10))
        for i, (label, value, color) in enumerate([
            ("Plantilla total", str(len(emps)), "#7C8CE6"),
            ("Activos", str(active), "#B8C3FF"),
            ("Salario medio", f"€ {avg_salary:,.0f}", "#8ED7FF"),
        ]):
            stats.columnconfigure(i, weight=1)
            draw_kpi_tile(stats, label, value, color).grid(row=0, column=i, sticky="nsew", padx=6)

        self._tree = make_treeview(self, [
            ("id",      "ID",       50,  "center"),
            ("name",    "Nombre",   200, "w"),
            ("role",    "Rol",      170, "w"),
            ("salary",  "Salario",  100, "e"),
            ("zone",    "Zona",     180, "w"),
            ("tech",    "Nivel téc.", 100, "center"),
            ("status",  "Estado",   100, "center"),
        ])
        self._tree.tag_configure("active", foreground="#B8C3FF")
        self._tree.tag_configure("inactive", foreground="#FF7D7A")
        self._tree.tag_configure("vacation", foreground="#F4D27C")
        self._tree.bind("<Double-1>", lambda _e: self._on_edit())
        self._tree.bind("<<TreeviewSelect>>", lambda _e: self._render_detail())

        self._detail = ttk.Frame(self, style="Card.TFrame", padding=(16, 12))
        self._detail.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Label(self._detail, text="Detalle seleccionado", style="Subtitle.TLabel").pack(anchor="w")
        row = ttk.Frame(self._detail, style="Card.TFrame")
        row.pack(anchor="w", pady=(8, 0))
        self._pill_status = StatusPill(row, "ESTADO: —", accent="#B8C3FF")
        self._pill_status.pack(side="left", padx=(0, 10))
        self._pill_role = StatusPill(row, "ROL: —", accent="#7C8CE6")
        self._pill_role.pack(side="left")
        self._detail_text = ttk.Label(self._detail, text="Selecciona un empleado para ver detalle.", style="Muted.TLabel")
        self._detail_text.pack(anchor="w", pady=(8, 0))
        self._refresh()

    def _enclosure_choices(self):
        choices = [("0 — Sin asignar", None)]
        for e in self._enc_repo.list_all():
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
        enc_map = {e.id: e.name for e in self._enc_repo.list_all()}
        query = self._q_var.get().strip().lower()
        role = self._role_filter.get()
        status = STATUS_VALUES.get(self._status_filter.get())
        for emp in self._svc.list_all():
            if query and query not in emp.name.lower():
                continue
            if role != ALL_LABEL and emp.role != role:
                continue
            if status and emp.status != status:
                continue
            self._tree.insert(
                "", "end", iid=str(emp.id),
                values=(emp.id, emp.name, emp.role, f"€ {emp.salary:,.2f}",
                        enc_map.get(emp.assigned_zone, "Sin asignar")
                        if emp.assigned_zone else "Sin asignar",
                        emp.technical_level, STATUS_LABELS.get(emp.status, emp.status)),
                tags=(emp.status,),
            )
        self._render_detail()

    def _render_detail(self):
        sel = self._tree.selection()
        if not sel:
            self._pill_status.set("ESTADO: —", accent="#B8C3FF")
            self._pill_role.set("ROL: —", accent="#7C8CE6")
            self._detail_text.configure(text="Selecciona un empleado para ver detalle.")
            return
        vals = self._tree.item(sel[0]).get("values", [])
        # id, name, role, salary, zone, tech, status
        try:
            name = vals[1]
            role = str(vals[2]).upper()
            salary = vals[3]
            tech = vals[5]
            status = STATUS_VALUES.get(str(vals[6]), str(vals[6])).upper()
        except Exception:
            return
        accent = {"ACTIVE": "#B8C3FF", "INACTIVE": "#FF7D7A", "VACATION": "#F4D27C"}.get(status, "#B8C3FF")
        estado_es = {"ACTIVE": "ACTIVO", "INACTIVE": "INACTIVO", "VACATION": "VACACIONES"}.get(status, status)
        self._pill_status.set(f"ESTADO: {estado_es}", accent=accent)
        self._pill_role.set(f"ROL: {role[:14]}", accent="#7C8CE6")
        self._detail_text.configure(text=f"{name} · {salary} · Nivel técnico: {tech}")

    def _form_fields(self):
        choices = self._enclosure_choices()
        labels = [c[0] for c in choices]
        return choices, [
            ("name",   "Nombre", "entry", None),
            ("role",   "Rol",    "combo",
             {"values": list(EMPLOYEE_ROLES), "default": EMPLOYEE_ROLES[0]}),
            ("salary", "Salario (€)", "entry",
             {"validate": tk_validate_float, "default": 1500}),
            ("zone_label", "Zona asignada", "combo",
             {"values": labels, "default": labels[0]}),
            ("technical_level", "Nivel técnico (1-5)", "spin",
             {"from_": 1, "to": 5, "default": 1, "validate": tk_validate_int}),
            ("status", "Estado", "combo",
             {"values": list(STATUS_LABELS.values()), "default": STATUS_LABELS["active"]}),
        ]

    def _selected(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un empleado.", parent=self)
            return None
        return int(sel[0])

    def _on_new(self):
        choices, fields = self._form_fields()
        dlg = FormDialog(self.winfo_toplevel(), "Nuevo empleado", fields)
        self.wait_window(dlg)
        if not dlg.result:
            return
        data = dict(dlg.result)
        data["status"] = STATUS_VALUES.get(data["status"], data["status"])
        data["assigned_zone"] = self._resolve(data.pop("zone_label"), choices)
        try:
            self._svc.create(data)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _on_edit(self):
        emp_id = self._selected()
        if emp_id is None:
            return
        from repositories.employee_repository import EmployeeRepository
        emp = EmployeeRepository().get(emp_id)
        if emp is None:
            return
        choices, fields = self._form_fields()
        labels = [c[0] for c in choices]
        sel_label = labels[0]
        for lbl, eid in choices:
            if eid == emp.assigned_zone:
                sel_label = lbl
                break
        initial = emp.to_dict()
        initial["status"] = STATUS_LABELS.get(initial["status"], initial["status"])
        initial["zone_label"] = sel_label
        dlg = FormDialog(self.winfo_toplevel(), f"Editar {emp.name}",
                         fields, initial=initial)
        self.wait_window(dlg)
        if not dlg.result:
            return
        data = dict(dlg.result)
        data["status"] = STATUS_VALUES.get(data["status"], data["status"])
        data["assigned_zone"] = self._resolve(data.pop("zone_label"), choices)
        try:
            self._svc.update(emp_id, data)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _on_delete(self):
        emp_id = self._selected()
        if emp_id is None:
            return
        if not messagebox.askyesno("Confirmar",
                                   f"¿Eliminar empleado #{emp_id}?", parent=self):
            return
        try:
            self._svc.delete(emp_id)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)
