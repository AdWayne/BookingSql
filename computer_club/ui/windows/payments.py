"""
ui/windows/payments.py  — client_name, pc_number, tariff_name, PC_STATUS
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ui.base_window import BaseWindow
from utils.widgets import styled_button, make_treeview
from utils.theme import *


class PaymentsWindow(BaseWindow):
    def __init__(self, master, db):
        super().__init__(master, "💳  Payments", 1020, 640)
        self.db = db
        self._build()

    def _build(self):
        left = tk.Frame(self.content, bg=BG_PANEL, width=370)
        left.pack(side="left", fill="y", padx=(14,0), pady=14)
        left.pack_propagate(False)

        tk.Label(left, text="Добавить платёж",
                 bg=BG_PANEL, fg=ACCENT4, font=FONT_HEAD).pack(pady=(14,6), padx=14, anchor="w")
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14)


        form = tk.Frame(left, bg=BG_PANEL)
        form.pack(padx=14, pady=14, fill="x")
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Бронирование", bg=BG_PANEL, fg=FG_MUTED,
                 font=FONT_SMALL).grid(row=0, column=0, sticky="w", pady=4, padx=2)

        self._bookings = self.db.fetchall("""
            SELECT b.booking_id,
                   cl.client_name,
                   c.pc_number,
                   TO_CHAR(b.start_time, 'YYYY-MM-DD HH24:MI'),
                   TO_CHAR(b.end_time,   'YYYY-MM-DD HH24:MI'),
                   t.price_per_hour
            FROM BOOKING  b
            JOIN CLIENT   cl ON cl.client_id  = b.client_id
            JOIN COMPUTER c  ON c.computer_id = b.computer_id
            JOIN TARIFF   t  ON t.tariff_id   = c.tariff_id
            ORDER BY b.booking_id DESC
        """)
        self.booking_var = tk.StringVar()
        cb = ttk.Combobox(
            form, textvariable=self.booking_var,
            values=[f"{b[0]}: {b[1]} – ПК {b[2]}" for b in self._bookings],
            state="readonly", font=FONT_BODY, width=30,
        )
        cb.grid(row=0, column=1, sticky="ew", pady=4)
        cb.bind("<<ComboboxSelected>>", self._auto_calc)

        tk.Label(form, text="Сумма (₸)", bg=BG_PANEL, fg=FG_MUTED,
                 font=FONT_SMALL).grid(row=1, column=0, sticky="w", pady=4, padx=2)
        self.amount_var = tk.StringVar()
        tk.Entry(form, textvariable=self.amount_var,
                 bg=BG_ENTRY, fg=ACCENT2, insertbackground=FG_MAIN,
                 font=("Segoe UI", 12, "bold"), relief="flat", bd=5, width=20).grid(
            row=1, column=1, sticky="ew", pady=4)

        self.calc_info = tk.Label(form, text="", bg=BG_PANEL, fg=FG_MUTED,
                                  font=FONT_SMALL, wraplength=230, justify="left")
        self.calc_info.grid(row=2, column=0, columnspan=2, sticky="w", pady=2)

        tk.Label(form, text="Способ", bg=BG_PANEL, fg=FG_MUTED,
                 font=FONT_SMALL).grid(row=3, column=0, sticky="w", pady=4, padx=2)
        self.method_var = tk.StringVar(value="Наличные")
        ttk.Combobox(form, textvariable=self.method_var,
                     values=["Наличные", "Карта", "Онлайн-перевод"],
                     state="readonly", font=FONT_BODY, width=20).grid(
            row=3, column=1, sticky="ew", pady=4)

        styled_button(form, "💳 Добавить платёж", self._pay, ACCENT4, 26).grid(
            row=4, column=0, columnspan=2, pady=16, sticky="ew")
        
        styled_button(form, "✅ Подтвердить оплату", self._confirm, ACCENT2, 26).grid(
        row=5, column=0, columnspan=2, pady=6, sticky="ew")

        right = tk.Frame(self.content, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=14)
        tk.Label(right, text="История платежей", bg=BG_DARK,
                 fg=FG_MUTED, font=FONT_SMALL).pack(anchor="w", padx=6)

        cols = [("id","ID",55),("booking","Бронь",70),("client","Клиент",160),
                ("pc","ПК",60),("amount","Сумма ₸",100),("method","Способ",130),("date","Дата",140)]
        self.tree = make_treeview(right, cols)
        self._load()

    def _confirm(self):
        selected = self.tree.focus()
        if not selected:
            return

        payment_id = self.tree.item(selected)["values"][0]

        booking = self.db.fetchone(
            "SELECT booking_id FROM PAYMENT WHERE payment_id = :1",
            [payment_id]
        )

        computer = self.db.fetchone(
            "SELECT computer_id FROM BOOKING WHERE booking_id = :1",
        [booking[0]]
        )

        self.db.execute(
            "UPDATE COMPUTER SET status_id = 2 WHERE computer_id = :1",
        [computer[0]]
        )

    # подтверждаем платеж
        self.db.execute(
            "UPDATE PAYMENT SET confirmed = 1 WHERE payment_id = :1",
        [payment_id]
        )

        self._load()

    def _auto_calc(self, event=None):
        sel = self.booking_var.get()
        if not sel:
            return
        booking_id = int(sel.split(":")[0])
        bk = next((b for b in self._bookings if b[0] == booking_id), None)
        if not bk:
            return
        fmt = "%Y-%m-%d %H:%M"
        hours = max((datetime.strptime(bk[4], fmt) -
                     datetime.strptime(bk[3], fmt)).total_seconds() / 3600, 0)
        rate  = float(bk[5])
        total = round(hours * rate, 2)
        self.amount_var.set(str(total))
        self.calc_info.config(text=f"{hours:.2f} ч × ₸{rate:.0f}/ч = ₸{total:.2f}")

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.db.fetchall("""
            SELECT p.payment_id,
                   p.booking_id,
                   cl.client_name,
                   c.pc_number,
                   p.amount,
                   p.payment_method,
                   TO_CHAR(p.payment_date, 'YYYY-MM-DD HH24:MI')
            FROM PAYMENT  p
            JOIN BOOKING  b  ON b.booking_id  = p.booking_id
            JOIN CLIENT   cl ON cl.client_id  = b.client_id
            JOIN COMPUTER c  ON c.computer_id = b.computer_id
            WHERE NVL(p.confirmed,0) = 0
            ORDER BY p.payment_id DESC
        """)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def _pay(self):
        sel = self.booking_var.get()
        if not sel:
            messagebox.showwarning("Выбор", "Выберите бронирование.", parent=self)
            return
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showwarning("Сумма", "Введите корректную сумму.", parent=self)
            return
        booking_id = int(sel.split(":")[0])
        self.db.execute(
            "INSERT INTO PAYMENT (booking_id, amount, payment_method) VALUES (:1, :2, :3)",
            [booking_id, amount, self.method_var.get()],
        )
        messagebox.showinfo("Успех", f"Платёж ₸{amount:,.2f} записан!", parent=self)
        self._load()