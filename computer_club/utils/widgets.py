"""
utils/widgets.py
────────────────
Переиспользуемые виджеты и хелперы, не зависящие от бизнес-логики:
  • styled_button   – плоская кнопка с hover-эффектом
  • make_treeview   – Treeview с тёмной темой и скроллбаром
  • label_entry     – пара Label + Entry на grid-родителе
"""

import tkinter as tk
from tkinter import ttk
from .theme import *


# ──────────────────────────────────────────────
def _lighten(hex_color: str) -> str:
    """Возвращает слегка осветлённый hex-цвет (для hover)."""
    r = min(255, int(hex_color[1:3], 16) + 30)
    g = min(255, int(hex_color[3:5], 16) + 30)
    b = min(255, int(hex_color[5:7], 16) + 30)
    return f"#{r:02x}{g:02x}{b:02x}"


def styled_button(parent, text: str, command, color=ACCENT, width=18) -> tk.Button:
    """Плоская кнопка с hover-подсветкой."""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=BG_DARK,
        activebackground=color,
        activeforeground=BG_DARK,
        font=FONT_BTN,
        relief="flat",
        cursor="hand2",
        padx=12,
        pady=7,
        width=width,
        bd=0,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def make_treeview(parent, columns: list) -> ttk.Treeview:
    """
    Создаёт тёмный Treeview со скроллбаром.
    columns = [(col_id, heading, width), ...]
    Возвращает объект ttk.Treeview.
    """
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.Treeview",
                    background=BG_PANEL,
                    foreground=FG_MAIN,
                    fieldbackground=BG_PANEL,
                    rowheight=28,
                    font=FONT_BODY)
    style.configure("Dark.Treeview.Heading",
                    background=BORDER,
                    foreground=FG_MAIN,
                    font=FONT_BTN)
    style.map("Dark.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", BG_DARK)])

    frame = tk.Frame(parent, bg=BG_PANEL)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    col_ids = [c[0] for c in columns]
    tree = ttk.Treeview(frame, columns=col_ids, show="headings",
                        style="Dark.Treeview")

    for col_id, heading, width in columns:
        tree.heading(col_id, text=heading)
        tree.column(col_id, width=width, minwidth=40, anchor="w")

    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)
    return tree


def label_entry(parent, text: str, row: int, col: int = 0,
                width: int = 28) -> tk.StringVar:
    """
    Размещает Label + Entry на grid-родителе.
    Возвращает StringVar, привязанный к Entry.
    """
    tk.Label(parent, text=text, bg=BG_PANEL, fg=FG_MUTED, font=FONT_SMALL,
             anchor="w").grid(row=row, column=col, sticky="w", pady=3, padx=4)
    var = tk.StringVar()
    tk.Entry(parent, textvariable=var, bg=BG_ENTRY, fg=FG_MAIN,
             insertbackground=FG_MAIN, font=FONT_BODY,
             relief="flat", bd=5, width=width).grid(
        row=row, column=col + 1, sticky="ew", pady=3, padx=4)
    return var
