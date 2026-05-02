"""Vista de Taquilla: venta de entradas con generación de localizador."""
import tkinter as tk
from tkinter import messagebox, ttk

from services.ticket_service import TicketService
from utils.constants import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BG_CARD,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    IVA_RATE,
    TICKET_TYPES,
)
from utils.exceptions import DinoReserveError
from views.crud_helpers import make_section_header, make_treeview
from views.ui_kit import make_status_pill
from views.ui_kit import StatusPill

TYPE_LABELS = {
    "normal":    "Normal",
    "child":     "Infantil",
    "vip":       "VIP",
    "fast_pass": "Pase Rápido",
}


class TicketView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._svc = TicketService()
        self._receipt_preview = None
        self._build()

    def _build(self):
        make_section_header(
            self, "Taquilla de entradas",
            "Venta con cálculo automático de IVA y generación de localizador único.",
            module_key="sales",
        )

        body = ttk.Frame(self, padding=(18, 0, 18, 12))
        body.pack(fill="x")

        # Tarjeta venta
        card = tk.Frame(body, bg=COLOR_BG_CARD, bd=0, highlightthickness=1, highlightbackground="#345d44")
        card.pack(side="left", fill="y", ipady=10, padx=(0, 16))

        tk.Label(card, text="Nueva venta", bg=COLOR_BG_CARD, fg=COLOR_ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=20, pady=(16, 12)
        )

        tk.Label(card, text="Visitante", bg=COLOR_BG_CARD,
                 fg=COLOR_TEXT).pack(anchor="w", padx=20)
        self._visitor = tk.StringVar()
        self._visitor.trace_add("write", lambda *_: self._update_receipt_preview())
        ttk.Entry(card, textvariable=self._visitor, width=32).pack(
            padx=20, pady=(2, 10), ipady=4
        )

        tk.Label(card, text="Tipo de entrada", bg=COLOR_BG_CARD,
                 fg=COLOR_TEXT).pack(anchor="w", padx=20)
        type_grid = tk.Frame(card, bg=COLOR_BG_CARD)
        type_grid.pack(fill="x", padx=20, pady=(4, 8))
        self._type = tk.StringVar(value="normal")
        for i, ttype in enumerate(TICKET_TYPES.keys()):
            rb = ttk.Radiobutton(
                type_grid,
                text=TYPE_LABELS.get(ttype, ttype),
                value=ttype,
                variable=self._type,
                command=self._update_summary,
            )
            rb.grid(row=i // 2, column=i % 2, sticky="w", padx=4, pady=2)

        # Resumen precio / IVA / total
        self._summary_frame = tk.Frame(card, bg=COLOR_BG_CARD)
        self._summary_frame.pack(fill="x", padx=20, pady=(4, 14))
        self._build_summary()
        self._receipt_preview = tk.Text(
            card, height=7, bg="#13291f", fg=COLOR_TEXT, borderwidth=0,
            font=("Consolas", 10), padx=8, pady=8
        )
        self._receipt_preview.pack(fill="x", padx=20, pady=(0, 10))
        self._update_receipt_preview()

        ttk.Button(card, text="🎟  Vender entrada", style="Accent.TButton",
                   command=self._sell).pack(fill="x", padx=20, pady=(0, 16))

        # Información lateral
        info = tk.Frame(body, bg=COLOR_BG_CARD, highlightthickness=1, highlightbackground="#345d44")
        info.pack(side="left", fill="both", expand=True)
        top_info = tk.Frame(info, bg=COLOR_BG_CARD)
        top_info.pack(fill="x", padx=16, pady=(16, 6))
        tk.Label(top_info, text="Tarifas vigentes", bg=COLOR_BG_CARD, fg=COLOR_ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        holder = ttk.Frame(top_info, style="Card.TFrame")
        holder.pack(side="right")
        make_status_pill(holder, "SINCRONIZACIÓN ACTIVA").pack()
        for code, price in TICKET_TYPES.items():
            tk.Label(
                info,
                text=f"• {TYPE_LABELS[code]:10s}  €{price:6.2f}  +  IVA {IVA_RATE*100:.0f}%  =  €{price*(1+IVA_RATE):6.2f}",
                bg=COLOR_BG_CARD, fg=COLOR_TEXT, font=("Consolas", 11),
                anchor="w",
            ).pack(anchor="w", pady=2, padx=16)
        tk.Label(
            info,
            text="\nLas entradas quedan registradas con un código único DR-XXXXXXXX\n"
                 "y la operación se guarda como una transacción atómica.",
            bg=COLOR_BG_CARD, fg=COLOR_TEXT_MUTED, justify="left",
        ).pack(anchor="w", pady=(8, 12), padx=16)

        # Tabla histórica
        ttk.Label(self, text="Ventas recientes", style="Subtitle.TLabel").pack(
            anchor="w", padx=28, pady=(6, 4)
        )
        self._tree = make_treeview(self, [
            ("id",       "ID",         50,  "center"),
            ("date",     "Fecha",      160, "w"),
            ("visitor",  "Visitante",  220, "w"),
            ("type",     "Tipo",       120, "center"),
            ("price",    "Precio",     90,  "e"),
            ("iva",      "IVA",        80,  "e"),
            ("total",    "Total",      90,  "e"),
            ("locator",  "Localizador",140, "center"),
        ])
        self._tree.bind("<<TreeviewSelect>>", lambda _e: self._render_detail())

        self._detail = ttk.Frame(self, style="Card.TFrame", padding=(16, 12))
        self._detail.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Label(self._detail, text="Detalle seleccionado", style="Subtitle.TLabel").pack(anchor="w")
        row = ttk.Frame(self._detail, style="Card.TFrame")
        row.pack(anchor="w", pady=(8, 0))
        self._pill_locator = StatusPill(row, "LOCALIZADOR: —", accent="#D9A441")
        self._pill_locator.pack(side="left", padx=(0, 10))
        self._pill_total = StatusPill(row, "TOTAL: —", accent="#2EF7B5")
        self._pill_total.pack(side="left", padx=(0, 10))
        self._pill_type = StatusPill(row, "TIPO: —", accent="#7FE7F5")
        self._pill_type.pack(side="left")

        actions = ttk.Frame(self._detail, style="Card.TFrame")
        actions.pack(anchor="w", pady=(10, 0))
        ttk.Button(actions, text="Copiar localizador", command=self._copy_locator).pack(side="left")
        self._detail_text = ttk.Label(self._detail, text="Selecciona una venta para ver detalles.", style="Muted.TLabel")
        self._detail_text.pack(anchor="w", pady=(8, 0))
        self._refresh()

    def _build_summary(self):
        for w in self._summary_frame.winfo_children():
            w.destroy()
        ttype = self._type.get()
        price = TICKET_TYPES.get(ttype, 0)
        iva = round(price * IVA_RATE, 2)
        total = round(price + iva, 2)
        rows = [
            ("Precio base", f"€ {price:.2f}"),
            (f"IVA ({IVA_RATE*100:.0f}%)", f"€ {iva:.2f}"),
            ("Total", f"€ {total:.2f}"),
        ]
        for label, value in rows:
            line = tk.Frame(self._summary_frame, bg=COLOR_BG_CARD)
            line.pack(fill="x", pady=2)
            tk.Label(line, text=label, bg=COLOR_BG_CARD, fg=COLOR_TEXT_MUTED).pack(side="left")
            tk.Label(line, text=value, bg=COLOR_BG_CARD, fg=COLOR_TEXT,
                     font=("Segoe UI", 11, "bold")).pack(side="right")

    def _update_summary(self):
        self._build_summary()
        self._update_receipt_preview()

    def _update_receipt_preview(self):
        if not self._receipt_preview:
            return
        ttype = self._type.get()
        price = TICKET_TYPES.get(ttype, 0.0)
        iva = round(price * IVA_RATE, 2)
        total = round(price + iva, 2)
        visitor = self._visitor.get().strip() or "<visitante>"
        receipt = (
            "SISTEMA DINORESERVE - VISTA PREVIA\n"
            "--------------------------------\n"
            f"Visitante: {visitor}\n"
            f"Entrada: {TYPE_LABELS.get(ttype, ttype)}\n"
            f"Base: € {price:.2f}\n"
            f"IVA:  € {iva:.2f}\n"
            f"TOTAL: € {total:.2f}\n"
            "--------------------------------\n"
            "Localizador: DR-XXXXXXXX\n"
        )
        self._receipt_preview.configure(state="normal")
        self._receipt_preview.delete("1.0", "end")
        self._receipt_preview.insert("1.0", receipt)
        self._receipt_preview.configure(state="disabled")

    def _sell(self):
        try:
            ticket = self._svc.sell_ticket(self._visitor.get(), self._type.get())
        except DinoReserveError as exc:
            messagebox.showerror("Error", exc.message, parent=self)
            return
        self._show_receipt_popup(
            locator=ticket.locator_code,
            visitor=ticket.visitor_name,
            ttype=TYPE_LABELS.get(ticket.ticket_type, ticket.ticket_type),
            base=ticket.price,
            iva=ticket.iva,
            total=ticket.total,
            date=ticket.sale_date,
        )
        self._visitor.set("")
        self._update_receipt_preview()
        self._refresh()

    def _refresh(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        for t in self._svc.list_all():
            self._tree.insert(
                "", "end",
                values=(t.id, t.sale_date, t.visitor_name,
                        TYPE_LABELS.get(t.ticket_type, t.ticket_type),
                        f"{t.price:.2f}", f"{t.iva:.2f}", f"{t.total:.2f}",
                        t.locator_code),
            )
        self._render_detail()

    def _copy_locator(self):
        if not self._tree.selection():
            return
        vals = self._tree.item(self._tree.selection()[0]).get("values", [])
        if len(vals) < 8:
            return
        locator = str(vals[7])
        self.clipboard_clear()
        self.clipboard_append(locator)

    def _render_detail(self):
        sel = self._tree.selection()
        if not sel:
            self._pill_locator.set("LOCALIZADOR: —", accent="#D9A441")
            self._pill_total.set("TOTAL: —", accent="#2EF7B5")
            self._pill_type.set("TIPO: —", accent="#7FE7F5")
            self._detail_text.configure(text="Selecciona una venta para ver detalles.")
            return
        vals = self._tree.item(sel[0]).get("values", [])
        try:
            visitor = vals[2]
            ttype = vals[3]
            total = vals[6]
            locator = vals[7]
            date = vals[1]
        except Exception:
            return
        self._pill_locator.set(f"LOCALIZADOR: {locator}", accent="#D9A441")
        self._pill_total.set(f"TOTAL: € {total}", accent="#2EF7B5")
        self._pill_type.set(f"TIPO: {ttype}", accent="#7FE7F5")
        self._detail_text.configure(text=f"{date} · {visitor}")

    def _show_receipt_popup(self, locator: str, visitor: str, ttype: str, base: float, iva: float, total: float, date: str):
        win = tk.Toplevel(self.winfo_toplevel())
        win.title("Recibo de venta")
        win.configure(bg=COLOR_BG)
        win.transient(self.winfo_toplevel())
        win.grab_set()
        win.resizable(False, False)

        wrap = ttk.Frame(win, style="Card.TFrame", padding=(18, 14))
        wrap.pack(fill="both", expand=True, padx=14, pady=14)
        ttk.Label(wrap, text="RECIBO / VENTA DE ENTRADA", style="Subtitle.TLabel").pack(anchor="w")
        ttk.Label(wrap, text="Operaciones Jurásicas · Punto de venta", style="Muted.TLabel").pack(anchor="w", pady=(2, 10))

        pills = ttk.Frame(wrap, style="Card.TFrame")
        pills.pack(anchor="w", pady=(0, 10))
        StatusPill(pills, f"LOCALIZADOR: {locator}", accent="#D9A441").pack(side="left", padx=(0, 10))
        StatusPill(pills, f"TOTAL: € {total:.2f}", accent="#2EF7B5").pack(side="left", padx=(0, 10))
        StatusPill(pills, f"TIPO: {ttype}", accent="#7FE7F5").pack(side="left")

        txt = tk.Text(
            wrap,
            height=10,
            bg="#0B1412",
            fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            font=("Consolas", 10),
            borderwidth=0,
            padx=10,
            pady=10,
        )
        txt.pack(fill="x")
        receipt = (
            "SISTEMA DINORESERVE — RECIBO\n"
            "----------------------------------------\n"
            f"FECHA:        {date}\n"
            f"VISITANTE:    {visitor}\n"
            f"TIPO:         {ttype}\n"
            "----------------------------------------\n"
            f"BASE:         € {base:.2f}\n"
            f"IVA:          € {iva:.2f}\n"
            f"TOTAL:        € {total:.2f}\n"
            "----------------------------------------\n"
            f"LOCALIZADOR:  {locator}\n"
        )
        txt.insert("1.0", receipt)
        txt.configure(state="disabled")

        actions = ttk.Frame(wrap, style="Card.TFrame")
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="Copiar localizador", command=lambda: (win.clipboard_clear(), win.clipboard_append(locator))).pack(side="left")
        ttk.Button(actions, text="Cerrar", style="Accent.TButton", command=win.destroy).pack(side="right")
