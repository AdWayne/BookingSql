"""
ui/app.py — главное окно, строка состояния с именами колонок не изменились
"""
import tkinter as tk
from db.connection import Database
from ui.windows    import ClientsWindow, ComputersWindow, BookingWindow, PaymentsWindow
from utils.theme   import *
from utils.widgets import styled_button


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Computer Club Booking System")
        self.geometry("680x520")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        self.db = Database()
        if not self.db.connect():
            self.destroy()
            return

        self.db.create_tables()
        self.db.seed_data()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._quit)

    def _build_ui(self):
        banner = tk.Frame(self, bg=BG_PANEL)
        banner.pack(fill="x")
        logo_row = tk.Frame(banner, bg=BG_PANEL)
        logo_row.pack(pady=28)
        tk.Label(logo_row, text="🖥", bg=BG_PANEL, fg=ACCENT,
                 font=("Segoe UI", 40)).pack(side="left", padx=(0, 12))
        col = tk.Frame(logo_row, bg=BG_PANEL)
        col.pack(side="left")
        tk.Label(col, text="Computer Club",  bg=BG_PANEL, fg=FG_MAIN,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(col, text="Booking System", bg=BG_PANEL, fg=ACCENT,
                 font=("Segoe UI", 14)).pack(anchor="w")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        tk.Label(self, text="Выберите модуль для работы",
                 bg=BG_DARK, fg=FG_MUTED, font=FONT_SMALL).pack(pady=(20, 10))

        nav = tk.Frame(self, bg=BG_DARK)
        nav.pack(expand=True)
        modules = [
            ("👤  Клиенты",      self._open_clients,   ACCENT),
            ("🖥  Компьютеры",   self._open_computers, ACCENT),
            ("📅  Бронирования", self._open_bookings,  ACCENT),
            ("💳  Платежи",      self._open_payments,  ACCENT4),
        ]
        for i, (label, cmd, color) in enumerate(modules):
            btn = tk.Button(nav, text=label, command=cmd,
                            bg=BG_PANEL, fg=FG_MAIN,
                            activebackground=color, activeforeground=BG_DARK,
                            font=("Segoe UI", 13, "bold"),
                            relief="flat", cursor="hand2", bd=0, width=26, height=2)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=c, fg=BG_DARK))
            btn.bind("<Leave>", lambda e, b=btn:          b.config(bg=BG_PANEL, fg=FG_MAIN))
            btn.grid(row=i // 2, column=i % 2, padx=14, pady=8, ipadx=10, ipady=6)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", pady=(10, 0))
        bar = tk.Frame(self, bg=BG_DARK)
        bar.pack(fill="x", pady=12)
        styled_button(bar, "Выход", self._quit, ACCENT3, 12).pack(side="right", padx=20)

        sb = tk.Frame(self, bg=BG_PANEL, height=26)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)

    def _open_clients(self):   ClientsWindow(self, self.db)
    def _open_computers(self): ComputersWindow(self, self.db)
    def _open_bookings(self):  BookingWindow(self, self.db)
    def _open_payments(self):  PaymentsWindow(self, self.db)

    def _quit(self):
        self.db.disconnect()
        self.destroy()
