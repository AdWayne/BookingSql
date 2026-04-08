"""
ui/base_window.py
──────────────────
Базовый класс для всех дочерних окон.
Обеспечивает единый «хром»: тёмный заголовок + контентная область.
"""

import tkinter as tk
from utils.theme import BG_DARK, BG_PANEL, BORDER, FG_MAIN, FONT_TITLE


class BaseWindow(tk.Toplevel):
    """
    Все модульные окна (Клиенты, Компьютеры, …) наследуют этот класс.
    После super().__init__() вся пользовательская разметка
    добавляется в self.content (tk.Frame).
    """

    def __init__(self, master, title: str, width: int = 900, height: int = 600):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # ── Заголовок ─────────────────────────
        header = tk.Frame(self, bg=BG_PANEL, height=55)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=title, bg=BG_PANEL, fg=FG_MAIN,
                 font=FONT_TITLE).pack(side="left", padx=20, pady=8)

        # ── Разделитель ───────────────────────
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # ── Контентная область ─────────────────
        self.content = tk.Frame(self, bg=BG_DARK)
        self.content.pack(fill="both", expand=True)
