"""Tabla reutilizable."""
from tkinter import ttk


class DataTable(ttk.Frame):
    def __init__(self, master, columns: list[tuple[str, str, int, str]], height: int = 14):
        super().__init__(master, style="Card.TFrame", padding=(10, 10))
        keys = [c[0] for c in columns]
        self.tree = ttk.Treeview(self, columns=keys, show="headings", height=height)
        for key, label, width, anchor in columns:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor=anchor)
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
