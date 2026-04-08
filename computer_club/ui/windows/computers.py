"""
ui/windows/computers.py  — PC_STATUS, club_name, status_name, tariff_name, pc_number
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ui.base_window import BaseWindow
from ui.dialogs.computer_dialog import ComputerDialog
from utils.widgets import styled_button, make_treeview
from utils.theme import *


class ComputersWindow(BaseWindow):
    def __init__(self, master, db):
        super().__init__(master, "🖥  Computers", 980, 580)
        self.db = db
        self._build()

    def _build(self):
        toolbar = tk.Frame(self.content, bg=BG_DARK, pady=10)
        toolbar.pack(fill="x", padx=14)
        styled_button(toolbar, "+ Добавить",       self._add,           ACCENT2).pack(side="left", padx=5)
        styled_button(toolbar, "⚙ Сменить статус", self._change_status, ACCENT ).pack(side="left", padx=5)
        styled_button(toolbar, "⟳ Обновить",       self._load,          ACCENT ).pack(side="left", padx=5)

        tk.Label(toolbar, text="  Клуб:", bg=BG_DARK, fg=FG_MUTED,
                 font=FONT_SMALL).pack(side="left", padx=(20, 4))
        self.club_var = tk.StringVar(value="Все")
        clubs = ["Все"] + [r[0] for r in self.db.fetchall(
            "SELECT club_name FROM CLUB ORDER BY club_id")]
        cb = ttk.Combobox(toolbar, textvariable=self.club_var,
                          values=clubs, state="readonly", width=20, font=FONT_BODY)
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda e: self._load())

        cols = [("id","ID",50),("number","Номер",90),("club","Клуб",190),
                ("status","Статус",110),("tariff","Тариф",160),("price","₸/час",80)]
        self.tree = make_treeview(self.content, cols)
        self._load()

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        club = self.club_var.get()
        if club == "Все":
            sql = """
                SELECT c.computer_id, c.pc_number,
                       cl.club_name,
                       s.status_name,
                       t.tariff_name,
                       t.price_per_hour
                FROM COMPUTER c
                JOIN CLUB      cl ON cl.club_id  = c.club_id
                JOIN PC_STATUS s  ON s.status_id = c.status_id
                JOIN TARIFF    t  ON t.tariff_id = c.tariff_id
                ORDER BY c.computer_id
            """
            rows = self.db.fetchall(sql)
        else:
            sql = """
                SELECT c.computer_id, c.pc_number,
                       cl.club_name, s.status_name, t.tariff_name, t.price_per_hour
                FROM COMPUTER c
                JOIN CLUB      cl ON cl.club_id  = c.club_id
                JOIN PC_STATUS s  ON s.status_id = c.status_id
                JOIN TARIFF    t  ON t.tariff_id = c.tariff_id
                WHERE cl.club_name = :1
                ORDER BY c.computer_id
            """
            rows = self.db.fetchall(sql, [club])
        for row in rows:
            self.tree.insert("", "end", values=row)

    def _add(self):
        dlg = ComputerDialog(self, self.db)
        self.wait_window(dlg)
        if dlg.result:
            number, club_id, status_id, tariff_id = dlg.result
            self.db.execute(
                "INSERT INTO COMPUTER (pc_number, club_id, status_id, tariff_id) "
                "VALUES (:1, :2, :3, :4)",
                [number, club_id, status_id, tariff_id],
            )
            self._load()

    def _change_status(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Выбор", "Сначала выберите компьютер.", parent=self)
            return
        computer_id = self.tree.item(sel[0])["values"][0]
        statuses = self.db.fetchall(
            "SELECT status_id, status_name FROM PC_STATUS ORDER BY status_id")
        hint = "\n".join(f"  {s[1]}" for s in statuses)
        choice = simpledialog.askstring(
            "Сменить статус",
            f"Новый статус для ПК #{computer_id}:\n{hint}",
            parent=self,
        )
        if choice:
            match = next((s for s in statuses
                          if s[1].lower() == choice.strip().lower()), None)
            if match:
                self.db.execute(
                    "UPDATE COMPUTER SET status_id = :1 WHERE computer_id = :2",
                    [match[0], computer_id],
                )
                self._load()
            else:
                messagebox.showwarning("Статус", "Такого статуса нет.", parent=self)
