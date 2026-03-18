import tkinter as tk
import keyboard
import win32gui

import process

_screen_width: int | None = None
_screen_height: int | None = None


def get_screen_dimensions() -> tuple[int, int]:
    global _screen_width, _screen_height
    if _screen_width is None or _screen_height is None:
        root = tk.Tk()
        root.withdraw()
        _screen_width = root.winfo_screenwidth()
        _screen_height = root.winfo_screenheight()
        root.destroy()
    return _screen_width, _screen_height


def center_window(win: tk.Tk | tk.Toplevel):
    win.update_idletasks()
    sw, sh = get_screen_dimensions()
    w = win.winfo_width()
    h = win.winfo_height()
    win.geometry(f"+{int((sw - w) / 2)}+{int((sh - h) / 2)}")


def bottom_right_window(win: tk.Tk | tk.Toplevel):
    win.update_idletasks()
    sw, sh = get_screen_dimensions()
    w = win.winfo_width()
    h = win.winfo_height()
    win.geometry(f"+{int(sw - w - 20)}+{int(sh - h - 60)}")


def steal_focus(widget: tk.BaseWidget):
    keyboard.press_and_release("alt")
    widget.focus_force()


def refocus_elden_ring():
    win32gui.SetForegroundWindow(process.ELDEN_RING_HWND)
