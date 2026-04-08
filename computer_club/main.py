"""
Computer Club Booking System
Entry point — запускать именно этот файл.

    python main.py
"""
from db.connection import Database
from ui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()

