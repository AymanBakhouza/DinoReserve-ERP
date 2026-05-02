"""Vista CRUD de Inventario, con +/- existencias."""
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from services.inventory_service import InventoryService
from utils.constants import COLOR_DANGER, COLOR_TEXT
from utils.exceptions import DinoReserveError
from utils.validators import tk_validate_float, tk_validate_int
from views.crud_helpers import FormDialog, make_section_header, make_toolbar, make_treeview
from views.ui_kit import draw_kpi_tile
from views.ui_kit import StatusPill

CATEGORIES = ("food_carnivore", "food_herbivore", "food_omnivore",
              "merchandise", "beverage", "medical", "logistics")
CATEGORY_LABELS = {
    "food_carnivore": "Comida carnívora",
    "food_herbivore": "Comida herbívora",
    "food_omnivore": "Comida omnívora",
    "merchandise": "Mercancía",
    "beverage": "Bebidas",
    "medical": "Médico",
    "logistics": "Logística",
}
CATEGORY_VALUES = {label: value for value, label in CATEGORY_LABELS.items()}
ALL_LABEL = "Todos"
STOCK_ALL = "Todos"
STOCK_LOW = "Existencias bajas"
STOCK_OK = "Correcto"


class InventoryView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._svc = InventoryService()
        self._q_var = tk.StringVar()
        self._category_filter = tk.StringVar(value=ALL_LABEL)
        self._stock_filter = tk.StringVar(value=STOCK_ALL)
        self._build()

    def _build(self):
        make_section_header(
            self, "Inventario y logística",
            "Existencias de tiendas, comida y suministros con alertas de mínimo.",
            module_key="logistics",
        )
        bar = make_toolbar(self)
        ttk.Entry(bar, textvariable=self._q_var, width=24).pack(side="left", padx=(0, 8))
        ttk.Combobox(bar, textvariable=self._category_filter, state="readonly",
                     values=[ALL_LABEL, *CATEGORY_LABELS.values()], width=18).pack(side="left", padx=(0, 8))
        ttk.Combobox(bar, textvariable=self._stock_filter, state="readonly",
                     values=[STOCK_ALL, STOCK_LOW, STOCK_OK], width=12).pack(side="left", padx=(0, 10))
        ttk.Button(bar, text="Filtrar", command=self._refresh).pack(side="left", padx=(0, 12))
        ttk.Button(bar, text="➕  Nuevo", style="Accent.TButton",
                   command=self._on_new).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="✏  Editar", command=self._on_edit).pack(side="left", padx=6)
        ttk.Button(bar, text="🗑  Eliminar", style="Danger.TButton",
                   command=self._on_delete).pack(side="left", padx=6)
        ttk.Button(bar, text="➕ Existencias",
                   command=lambda: self._adjust_stock("add")).pack(side="left", padx=6)
        ttk.Button(bar, text="➖ Existencias",
                   command=lambda: self._adjust_stock("reduce")).pack(side="left", padx=6)
        ttk.Button(bar, text="🔄  Refrescar",
                   command=self._refresh).pack(side="right")

        items = self._svc.list_all()
        low_count = len([i for i in items if i.is_low_stock()])
        total_qty = sum(i.quantity for i in items)
        stats = ttk.Frame(self, style="Card.TFrame", padding=(14, 10))
        stats.pack(fill="x", padx=12, pady=(0, 10))
        for i, (label, value, color) in enumerate([
            ("Ítems", str(len(items)), "#E8892B"),
            ("Unidades totales", f"{total_qty:,}", "#FFB366"),
            ("Existencias bajas", str(low_count), "#FF7D7A" if low_count else "#F5D07C"),
        ]):
            stats.columnconfigure(i, weight=1)
            draw_kpi_tile(stats, label, value, color).grid(row=0, column=i, sticky="nsew", padx=6)

        self._tree = make_treeview(self, [
            ("id",       "ID",         50,  "center"),
            ("name",     "Ítem",       220, "w"),
            ("category", "Categoría",  150, "w"),
            ("qty",      "Cantidad",   90,  "center"),
            ("min",      "Mínimo",     90,  "center"),
            ("supplier", "Proveedor",  150, "w"),
            ("price",    "Precio",     90,  "e"),
            ("status",   "Estado",     130, "center"),
        ])
        self._tree.tag_configure("low", foreground=COLOR_DANGER)
        self._tree.tag_configure("ok", foreground=COLOR_TEXT)
        self._tree.tag_configure("low", background="#1E1414")
        self._tree.tag_configure("ok", background="#0F1E1A")
        self._tree.bind("<Double-1>", lambda _e: self._on_edit())
        self._tree.bind("<<TreeviewSelect>>", lambda _e: self._render_detail())

        self._detail = ttk.Frame(self, style="Card.TFrame", padding=(16, 12))
        self._detail.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Label(self._detail, text="Detalle seleccionado", style="Subtitle.TLabel").pack(anchor="w")
        row = ttk.Frame(self._detail, style="Card.TFrame")
        row.pack(anchor="w", pady=(8, 0))
        self._pill_stock = StatusPill(row, "EXISTENCIAS: —", accent="#FFB366")
        self._pill_stock.pack(side="left", padx=(0, 10))
        self._pill_category = StatusPill(row, "CATEGORÍA: —", accent="#E8892B")
        self._pill_category.pack(side="left")
        self._detail_text = ttk.Label(self._detail, text="Selecciona un ítem para ver detalle.", style="Muted.TLabel")
        self._detail_text.pack(anchor="w", pady=(8, 0))
        self._refresh()

    def _refresh(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        query = self._q_var.get().strip().lower()
        category = CATEGORY_VALUES.get(self._category_filter.get())
        stock = self._stock_filter.get()
        for it in self._svc.list_all():
            if query and query not in f"{it.item_name} {it.supplier or ''}".lower():
                continue
            if category and it.category != category:
                continue
            if stock == STOCK_LOW and not it.is_low_stock():
                continue
            if stock == STOCK_OK and it.is_low_stock():
                continue
            tag = "low" if it.is_low_stock() else "ok"
            status_text = "Existencias bajas" if it.is_low_stock() else "Correcto"
            self._tree.insert(
                "", "end", iid=str(it.id),
                values=(it.id, it.item_name, CATEGORY_LABELS.get(it.category, it.category), it.quantity,
                        it.minimum_stock, it.supplier or "—",
                        f"€ {it.price:.2f}", status_text),
                tags=(tag,),
            )
        self._render_detail()

    def _render_detail(self):
        sel = self._tree.selection()
        if not sel:
            self._pill_stock.set("EXISTENCIAS: —", accent="#FFB366")
            self._pill_category.set("CATEGORÍA: —", accent="#E8892B")
            self._detail_text.configure(text="Selecciona un ítem para ver detalle.")
            return
        vals = self._tree.item(sel[0]).get("values", [])
        # id, name, category, qty, min, supplier, price, status
        try:
            name = vals[1]
            category = str(vals[2]).upper()
            qty = int(vals[3])
            mn = int(vals[4])
            status = str(vals[7]).upper()
        except Exception:
            return
        is_low = "BAJO" in status or qty < mn
        self._pill_stock.set("EXISTENCIAS: BAJAS" if is_low else "EXISTENCIAS: CORRECTAS", accent="#FF7D7A" if is_low else "#59F3BE")
        self._pill_category.set(f"CATEGORÍA: {category[:12]}", accent="#E8892B")
        self._detail_text.configure(text=f"{name} · Cantidad: {qty} · Mínimo: {mn}")

    def _form_fields(self):
        return [
            ("item_name",     "Nombre del ítem", "entry", None),
            ("category",      "Categoría",       "combo",
             {"values": list(CATEGORY_LABELS.values()), "default": CATEGORY_LABELS[CATEGORIES[0]]}),
            ("quantity",      "Cantidad",        "spin",
             {"from_": 0, "to": 1_000_000, "default": 0, "validate": tk_validate_int}),
            ("minimum_stock", "Existencias mínimas",    "spin",
             {"from_": 0, "to": 1_000_000, "default": 0, "validate": tk_validate_int}),
            ("supplier",      "Proveedor",       "entry", None),
            ("price",         "Precio (€)",      "entry",
             {"validate": tk_validate_float, "default": 0}),
        ]

    def _selected(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un ítem.", parent=self)
            return None
        return int(sel[0])

    def _on_new(self):
        dlg = FormDialog(self.winfo_toplevel(), "Nuevo ítem de inventario",
                         self._form_fields())
        self.wait_window(dlg)
        if not dlg.result:
            return
        try:
            data = dict(dlg.result)
            data["category"] = CATEGORY_VALUES.get(data["category"], data["category"])
            self._svc.create(data)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _on_edit(self):
        item_id = self._selected()
        if item_id is None:
            return
        from repositories.inventory_repository import InventoryRepository
        item = InventoryRepository().get(item_id)
        if item is None:
            return
        initial = item.to_dict()
        initial["category"] = CATEGORY_LABELS.get(initial["category"], initial["category"])
        dlg = FormDialog(self.winfo_toplevel(), f"Editar {item.item_name}",
                         self._form_fields(), initial=initial)
        self.wait_window(dlg)
        if not dlg.result:
            return
        try:
            data = dict(dlg.result)
            data["category"] = CATEGORY_VALUES.get(data["category"], data["category"])
            self._svc.update(item_id, data)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _on_delete(self):
        item_id = self._selected()
        if item_id is None:
            return
        if not messagebox.askyesno(
            "Confirmar", f"¿Eliminar ítem #{item_id}?", parent=self
        ):
            return
        try:
            self._svc.delete(item_id)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)

    def _adjust_stock(self, mode: str):
        item_id = self._selected()
        if item_id is None:
            return
        prompt = "Cantidad a añadir:" if mode == "add" else "Cantidad a reducir:"
        qty = simpledialog.askinteger("Existencias", prompt, minvalue=1, parent=self)
        if not qty:
            return
        try:
            if mode == "add":
                self._svc.add_stock(item_id, qty)
            else:
                self._svc.reduce_stock(item_id, qty)
            self._refresh()
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)
