"""
ui/dialogs/computer_dialog.py  — club_name, status_name, tariff_name, PC_STATUS
"""
import tkinter as tk
from tkinter import ttk, messagebox
from utils.widgets import label_entry, styled_button
from utils.theme import *


class ComputerDialog(tk.Toplevel):
    def __init__(self, master, db):
        super().__init__(master)
        self.title("Добавить компьютер")
        self.configure(bg=BG_PANEL)
        self.geometry("420x290")
        self.resizable(False, False)
        self.result = None
        self.db = db
        self.grab_set()
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=BG_PANEL)
        frm.pack(padx=20, pady=20, fill="both", expand=True)
        frm.columnconfigure(1, weight=1)

        self.number = label_entry(frm, "Номер ПК", 0, width=22)

        self._lbl(frm, "Клуб", 1)
        clubs = self.db.fetchall("SELECT club_id, club_name FROM CLUB ORDER BY club_id")
        self._clubs = clubs
        self.club_var = tk.StringVar()
        cb = ttk.Combobox(frm, textvariable=self.club_var,
                          values=[f"{c[0]}: {c[1]}" for c in clubs],
                          state="readonly", font=FONT_BODY)
        cb.grid(row=1, column=1, sticky="ew", pady=3, padx=4)
        if clubs: cb.current(0)

        self._lbl(frm, "Статус", 2)
        statuses = self.db.fetchall("SELECT status_id, status_name FROM PC_STATUS ORDER BY status_id")
        self._statuses = statuses
        self.status_var = tk.StringVar()
        cb2 = ttk.Combobox(frm, textvariable=self.status_var,
                            values=[f"{s[0]}: {s[1]}" for s in statuses],
                            state="readonly", font=FONT_BODY)
        cb2.grid(row=2, column=1, sticky="ew", pady=3, padx=4)
        if statuses: cb2.current(0)

        self._lbl(frm, "Тариф", 3)
        tariffs = self.db.fetchall("SELECT tariff_id, tariff_name FROM TARIFF ORDER BY tariff_id")
        self._tariffs = tariffs
        self.tariff_var = tk.StringVar()
        cb3 = ttk.Combobox(frm, textvariable=self.tariff_var,
                            values=[f"{t[0]}: {t[1]}" for t in tariffs],
                            state="readonly", font=FONT_BODY)
        cb3.grid(row=3, column=1, sticky="ew", pady=3, padx=4)
        if tariffs: cb3.current(0)

        styled_button(frm, "Сохранить", self._save, ACCENT2, 14).grid(
            row=4, column=0, columnspan=2, pady=16)

    @staticmethod
    def _lbl(p, t, r):
        tk.Label(p, text=t, bg=BG_PANEL, fg=FG_MUTED,
                 font=FONT_SMALL).grid(row=r, column=0, sticky="w", pady=3, padx=4)

    def _save(self):
        number = self.number.get().strip()
        if not number:
            messagebox.showwarning("Валидация", "Номер ПК обязателен.", parent=self)
            return
        self.result = (
            number,
            int(self.club_var.get().split(":")[0]),
            int(self.status_var.get().split(":")[0]),
            int(self.tariff_var.get().split(":")[0]),
        )
        self.destroy()
