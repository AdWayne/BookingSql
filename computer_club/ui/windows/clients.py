"""
ui/windows/clients.py  — колонка client_name (было name)
"""
import tkinter as tk
from tkinter import messagebox
from ui.base_window import BaseWindow
from ui.dialogs.client_dialog import ClientDialog
from utils.widgets import styled_button, make_treeview
from utils.theme import *


class ClientsWindow(BaseWindow):
    def __init__(self, master, db):
        super().__init__(master, "👤  Clients", 860, 560)
        self.db = db
        self._build()

    def _build(self):
        toolbar = tk.Frame(self.content, bg=BG_DARK, pady=10)
        toolbar.pack(fill="x", padx=14)
        styled_button(toolbar, "+ Добавить",  self._add,    ACCENT2).pack(side="left", padx=5)
        styled_button(toolbar, "✕ Удалить",   self._delete, ACCENT3).pack(side="left", padx=5)
        styled_button(toolbar, "⟳ Обновить",  self._load,   ACCENT ).pack(side="left", padx=5)

        cols = [("id","ID",50),("name","Имя",220),("phone","Телефон",150),("email","Email",280)]
        self.tree = make_treeview(self.content, cols)
        self._load()

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.db.fetchall(
            "SELECT client_id, client_name, phone, email FROM CLIENT ORDER BY client_id"
        )
        for row in rows:
            self.tree.insert("", "end", values=row)

    def _add(self):
        dlg = ClientDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            name, phone, email = dlg.result
            self.db.execute(
                "INSERT INTO CLIENT (client_name, phone, email) VALUES (:1, :2, :3)",
                [name, phone, email],
            )
            self._load()

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Выбор", "Сначала выберите клиента.", parent=self)
            return
        client_id = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Подтверждение", f"Удалить клиента #{client_id}?", parent=self):
            self.db.execute("DELETE FROM CLIENT WHERE client_id = :1", [client_id])
            self._load()
