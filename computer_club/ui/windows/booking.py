"""
ui/windows/booking.py  — client_name, pc_number, club_name, PC_STATUS
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ui.base_window import BaseWindow
from utils.widgets import styled_button, make_treeview
from utils.theme import *


class BookingWindow(BaseWindow):
    def __init__(self, master, db):
        super().__init__(master, "📅  Bookings", 1000, 640)
        self.db = db
        self._build()

    def _build(self):
        # ── Левая панель: форма ───────────────────────────────────────────
        left = tk.Frame(self.content, bg=BG_PANEL, width=350)
        left.pack(side="left", fill="y", padx=(14, 0), pady=14)
        left.pack_propagate(False)

        tk.Label(left, text="Новое бронирование",
                 bg=BG_PANEL, fg=ACCENT, font=FONT_HEAD).pack(pady=(14,6), padx=14, anchor="w")
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14)

        form = tk.Frame(left, bg=BG_PANEL)
        form.pack(padx=14, pady=14, fill="x")
        form.columnconfigure(1, weight=1)

        # Клиент
        self._lbl(form, "Клиент", 0)
        clients = self.db.fetchall(
            "SELECT client_id, client_name FROM CLIENT ORDER BY client_name")
        self._clients = clients
        self.client_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.client_var,
                     values=[f"{c[0]}: {c[1]}" for c in clients],
                     state="readonly", font=FONT_BODY, width=28).grid(
            row=0, column=1, sticky="ew", pady=4)

        # Компьютер
        self._lbl(form, "Компьютер", 1)
        computers = self.db.fetchall(
            "SELECT c.computer_id, c.pc_number, cl.club_name "
            "FROM COMPUTER c JOIN CLUB cl ON cl.club_id = c.club_id "
            "ORDER BY c.computer_id")
        self._computers = computers
        self.computer_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.computer_var,
                     values=[f"{c[0]}: {c[1]} ({c[2]})" for c in computers],
                     state="readonly", font=FONT_BODY, width=28).grid(
            row=1, column=1, sticky="ew", pady=4)

        # Время
        self._lbl(form, "Начало (ГГГГ-ММ-ДД ЧЧ:ММ)", 2)
        self.start_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        self._entry(form, self.start_var, 3)

        self._lbl(form, "Конец  (ГГГГ-ММ-ДД ЧЧ:ММ)", 4)
        self.end_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:00"))
        self._entry(form, self.end_var, 5)

        self.avail_lbl = tk.Label(form, text="", bg=BG_PANEL, font=FONT_SMALL, anchor="w")
        self.avail_lbl.grid(row=6, column=0, columnspan=2, sticky="w", pady=6)

        styled_button(form, "✔ Проверить доступность",
                      self._check, ACCENT, 26).grid(row=7, column=0, columnspan=2, pady=4, sticky="ew")
        styled_button(form, "+ Создать бронирование",
                      self._create, ACCENT2, 26).grid(row=8, column=0, columnspan=2, pady=4, sticky="ew")

        # ── Правая панель: таблица ────────────────────────────────────────
        right = tk.Frame(self.content, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=14)
        tk.Label(right, text="Все бронирования", bg=BG_DARK, fg=FG_MUTED,
                 font=FONT_SMALL).pack(anchor="w", padx=6)

        cols = [("id","ID",50),("client","Клиент",160),("pc","ПК",70),
                ("club","Клуб",160),("start","Начало",140),("end","Конец",140)]
        self.tree = make_treeview(right, cols)
        self._load()

    @staticmethod
    def _lbl(p, t, r):
        tk.Label(p, text=t, bg=BG_PANEL, fg=FG_MUTED, font=FONT_SMALL).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(8,0), padx=2)

    @staticmethod
    def _entry(p, var, r):
        tk.Entry(p, textvariable=var, bg=BG_ENTRY, fg=FG_MAIN,
                 insertbackground=FG_MAIN, font=FONT_BODY, relief="flat", bd=5).grid(
            row=r, column=0, columnspan=2, sticky="ew", pady=3, padx=2)

    def _parse_times(self):
        fmt = "%Y-%m-%d %H:%M"
        try:
            return (datetime.strptime(self.start_var.get().strip(), fmt),
                    datetime.strptime(self.end_var.get().strip(), fmt))
        except ValueError:
            messagebox.showwarning("Формат", "Используйте ГГГГ-ММ-ДД ЧЧ:ММ", parent=self)
            return None, None

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.db.fetchall("""
            SELECT b.booking_id,
                   cl.client_name,
                   c.pc_number,
                   club.club_name,
                   TO_CHAR(b.start_time, 'YYYY-MM-DD HH24:MI'),
                   TO_CHAR(b.end_time,   'YYYY-MM-DD HH24:MI')
            FROM BOOKING  b
            JOIN CLIENT   cl   ON cl.client_id   = b.client_id
            JOIN COMPUTER c    ON c.computer_id  = b.computer_id
            JOIN CLUB     club ON club.club_id    = c.club_id
            ORDER BY b.start_time DESC
        """)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def _check(self):
        if not self.computer_var.get():
            messagebox.showwarning("Выбор", "Выберите компьютер.", parent=self)
            return
        start, end = self._parse_times()
        if not start:
            return
        computer_id = int(self.computer_var.get().split(":")[0])
        conflict = self.db.fetchone("""
            SELECT COUNT(*) FROM BOOKING
            WHERE computer_id = :1
              AND start_time  < :2
              AND end_time    > :3
        """, [computer_id, end, start])
        if conflict and conflict[0] > 0:
            self.avail_lbl.config(text="✕  Занят — временной конфликт", fg=ACCENT3)
        else:
            self.avail_lbl.config(text="✔  Доступен!", fg=ACCENT2)

    def _create(self):
        if not self.client_var.get() or not self.computer_var.get():
            messagebox.showwarning("Выбор", "Выберите клиента и компьютер.", parent=self)
            return
        start, end = self._parse_times()
        if not start or end <= start:
            messagebox.showwarning("Время", "Конец должен быть позже начала.", parent=self)
            return

        client_id   = int(self.client_var.get().split(":")[0])
        computer_id = int(self.computer_var.get().split(":")[0])

        conflict = self.db.fetchone("""
            SELECT COUNT(*) FROM BOOKING
            WHERE computer_id = :1
              AND start_time  < :2
              AND end_time    > :3
        """, [computer_id, end, start])
        if conflict and conflict[0] > 0:
            messagebox.showerror("Конфликт", "Компьютер уже забронирован на это время.", parent=self)
            return

        self.db.execute(
            "INSERT INTO BOOKING (client_id, computer_id, start_time, end_time) "
            "VALUES (:1, :2, :3, :4)",
            [client_id, computer_id, start, end],
        )
        # status_id=2 → 'In Use'
        self.db.execute(
            "UPDATE COMPUTER SET status_id = 2 WHERE computer_id = :1", [computer_id]
        )
        messagebox.showinfo("Успех", "Бронирование создано!", parent=self)
        self.avail_lbl.config(text="")
        self._load()
