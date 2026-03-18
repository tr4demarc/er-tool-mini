import tkinter as tk
import threading
from ctypes import windll
import time

from saves import savestate
from ui.util import *

_last_selected_savestate: str | None = None
_current_notify_root: tk.Tk | None = None  # track to avoid overlapping
_current_notify_lock = threading.Lock()


# Set DPI awareness for better scaling on high-DPI displays
windll.shcore.SetProcessDpiAwareness(2)


def notify(message: str, duration_ms: int = 2000):
    """Show a temporary overlay notification with the given message."""
    global _current_notify_root

    with _current_notify_lock:
        if _current_notify_root:
            try:
                _current_notify_root.after(0, _current_notify_root.destroy)
            except Exception:
                pass
            _current_notify_root = None

    def _show():
        global _current_notify_root
        time.sleep(0.05)  # let previous mainloop exit cleanly
        root = tk.Tk()
        with _current_notify_lock:
            _current_notify_root = root
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.configure(bg="black", cursor="none")
        root.attributes("-transparentcolor", "black")
        tk.Label(
            root,
            text=message,
            fg="white",
            bg="black",
            font=("Helvetica", 10),
            padx=20,
            pady=10,
        ).pack()
        root.update_idletasks()
        sw, sh = get_screen_dimensions()
        root.geometry(f"+{int(sw * 0.8)}+{int(sh * 0.8)}")
        root.after(duration_ms, root.destroy)
        root.mainloop()
        with _current_notify_lock:
            _current_notify_root = None

    threading.Thread(target=_show, daemon=True).start()


def show_import_savestate():
    def _show():
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.9)
        root.configure(bg="black", cursor="none")

        tk.Label(
            root,
            text="Save state name:",
            fg="white",
            bg="black",
            font=("Helvetica", 14),
        ).pack(padx=20, pady=(15, 5))

        entry = tk.Entry(
            root,
            font=("Helvetica", 14),
            bg="#222222",
            fg="white",
            insertbackground="white",
        )
        entry.pack(padx=20, pady=(0, 10))

        def confirm(event=None):
            name = entry.get().strip()
            if name:
                root.destroy()
                savestate.import_savestate(name)

        def cancel(event=None):
            root.destroy()
            refocus_elden_ring()

        entry.bind("<Return>", confirm)
        entry.bind("<Escape>", cancel)

        bottom_right_window(root)
        steal_focus(entry)

        root.mainloop()
        refocus_elden_ring()

    threading.Thread(target=_show, daemon=True).start()


class _SavestateAdminWindow:
    def __init__(self):
        self.last_selected = _last_selected_savestate
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.9)
        self.root.configure(bg="black", cursor="none")

        tk.Label(
            self.root,
            text="Load save state:",
            fg="white",
            bg="black",
            font=("Helvetica", 14),
        ).pack(padx=20, pady=(15, 5))

        self.listbox = tk.Listbox(
            self.root,
            font=("Helvetica", 14),
            bg="#222222",
            fg="white",
            selectbackground="#444444",
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
        )
        self.listbox.pack(padx=20, pady=(0, 10))
        self.listbox.bind("<Return>", self.confirm)
        self.listbox.bind("<Escape>", self.cancel)
        self.listbox.bind("<Control-l>", self.cancel)
        self.listbox.bind("<F2>", self.rename)
        self.listbox.bind("<Delete>", self.delete)
        self.listbox.bind("<Prior>", lambda e: self.move_savestate(direction="up"))
        self.listbox.bind("<Next>", lambda e: self.move_savestate(direction="down"))

        self.refresh_list(self.last_selected)
        bottom_right_window(self.root)
        steal_focus(self.listbox)

    def run(self):
        self.root.mainloop()
        refocus_elden_ring()

    def refresh_list(self, select_name: str | None = None):
        savestates = savestate.get_savestates()
        self.listbox.delete(0, tk.END)
        for s in savestates:
            self.listbox.insert(tk.END, s)
        idx = (
            savestates.index(select_name)
            if select_name and select_name in savestates
            else 0
        )
        self.listbox.selection_set(idx)
        self.listbox.activate(idx)
        self.listbox.see(idx)

    def selected_name(self) -> str:
        selection = self.listbox.curselection()
        return self.listbox.get(selection[0])

    def move_savestate(self, direction: str, event=None):
        selected_name = self.selected_name()
        savestates = savestate.get_savestates()
        selected_index = savestates.index(selected_name)
        savestates.pop(selected_index)
        if direction == "up":
            new_index = max(0, selected_index - 1)
        if direction == "down":
            new_index = min(len(savestates), selected_index + 1)
        savestates.insert(new_index, selected_name)
        savestate.update_savestates_order(savestates)
        self.root.after(0, lambda: self.refresh_list(selected_name))

    def confirm(self, event=None):

        global _last_selected_savestate
        name = self.selected_name()
        if name:
            _last_selected_savestate = name
            self.root.destroy()
            savestate.load_savestate(name)

    def cancel(self, event=None):
        self.root.destroy()
        refocus_elden_ring()

    def rename(self, event=None):
        old_name = self.selected_name()
        if not old_name:
            return

        win = tk.Toplevel(self.root)
        win.withdraw()
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.9)
        win.configure(bg="black", cursor="none")

        tk.Label(
            win,
            text=f"Rename '{old_name}':",
            fg="white",
            bg="black",
            font=("Helvetica", 14),
        ).pack(padx=20, pady=(15, 5))

        entry = tk.Entry(
            win,
            font=("Helvetica", 14),
            bg="#222222",
            fg="white",
            insertbackground="white",
        )
        entry.insert(0, old_name)
        entry.select_range(0, tk.END)
        entry.pack(padx=20, pady=(0, 10))

        def confirm_rename(event=None):
            new_name = entry.get().strip()
            if new_name and new_name != old_name:
                savestate.rename_savestate(old_name, new_name)
            win.destroy()
            self.refresh_list(new_name if new_name else old_name)
            self.listbox.focus_force()

        entry.bind("<Return>", confirm_rename)
        entry.bind("<Escape>", lambda e: [win.destroy(), self.listbox.focus_force()])

        center_window(win)
        win.deiconify()
        steal_focus(entry)

    def delete(self, event=None):
        name = self.selected_name()
        if not name:
            return

        win = tk.Toplevel(self.root)
        win.withdraw()
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.9)
        win.configure(bg="black", cursor="none")

        tk.Label(
            win,
            text=f"Are you sure you want to delete\n'{name}'?",
            fg="white",
            bg="black",
            font=("Helvetica", 14),
            padx=20,
            pady=15,
        ).pack()

        btn_frame = tk.Frame(win, bg="black")
        btn_frame.pack(pady=(0, 15))

        def confirm_delete():
            savestate.delete_savestate(name)
            win.destroy()
            remaining = savestate.get_savestates()
            if not remaining:
                self.root.destroy()
            else:
                self.refresh_list()
                self.listbox.focus_force()

        def cancel_delete():
            win.destroy()
            self.listbox.focus_force()

        yes_btn = tk.Button(
            btn_frame,
            text="Yes",
            font=("Helvetica", 12),
            bg="#550000",
            fg="white",
            activebackground="#880000",
            relief="flat",
            padx=15,
            command=confirm_delete,
        )
        yes_btn.pack(side=tk.LEFT, padx=(0, 10))

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=("Helvetica", 12),
            bg="#222222",
            fg="white",
            activebackground="#444444",
            relief="flat",
            padx=15,
            command=cancel_delete,
        )
        cancel_btn.pack(side=tk.LEFT)

        yes_btn.bind("<Left>", lambda e: cancel_btn.focus_set())
        yes_btn.bind("<Right>", lambda e: cancel_btn.focus_set())
        cancel_btn.bind("<Left>", lambda e: yes_btn.focus_set())
        cancel_btn.bind("<Right>", lambda e: yes_btn.focus_set())
        yes_btn.bind("<Return>", lambda e: confirm_delete())
        cancel_btn.bind("<Return>", lambda e: cancel_delete())
        win.bind("<Escape>", lambda e: cancel_delete())

        center_window(win)
        win.deiconify()
        steal_focus(yes_btn)


def administer_savestates():
    savestates = savestate.get_savestates()
    if not savestates:
        notify("No save states found")
        return

    def _show():
        _SavestateAdminWindow().run()

    threading.Thread(target=_show, daemon=True).start()
