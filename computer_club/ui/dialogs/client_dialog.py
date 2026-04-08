"""
ui/dialogs/client_dialog.py
────────────────────────────
Модальный диалог добавления клиента.
После закрытия результат доступен в dlg.result = (name, phone, email) или None.
"""

import tkinter as tk
from tkinter import messagebox

from utils.widgets import label_entry, styled_button
from utils.theme import BG_PANEL, ACCENT2


class ClientDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Добавить клиента")
        self.configure(bg=BG_PANEL)
        self.geometry("380x220")
        self.resizable(False, False)
        self.result = None
        self.grab_set()
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=BG_PANEL)
        frm.pack(padx=20, pady=20, fill="both", expand=True)
        frm.columnconfigure(1, weight=1)

        self.name  = label_entry(frm, "ФИО",     0, width=26)
        self.phone = label_entry(frm, "Телефон", 1, width=26)
        self.email = label_entry(frm, "Email",   2, width=26)

        styled_button(frm, "Сохранить", self._save, ACCENT2, 14).grid(
            row=3, column=0, columnspan=2, pady=16)

    def _save(self):
        name = self.name.get().strip()
        if not name:
            messagebox.showwarning("Валидация", "ФИО обязательно.", parent=self)
            return
        self.result = (name, self.phone.get().strip(), self.email.get().strip())
        self.destroy()
