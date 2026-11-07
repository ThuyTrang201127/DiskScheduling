"""Điểm khởi chạy ứng dụng Disk Scheduling Simulator."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import messagebox


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        from gui import run_app

        run_app()
    except ModuleNotFoundError as error:
        if error.name != "matplotlib":
            raise
        message = (
            "Chưa cài Matplotlib. Mở Terminal tại thư mục project và chạy:\n"
            "python -m pip install -r requirements.txt"
        )
        print(message, file=sys.stderr)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Thiếu thư viện", message, parent=root)
            root.destroy()
        except tk.TclError:
            pass


if __name__ == "__main__":
    main()
