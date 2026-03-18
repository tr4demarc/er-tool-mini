import win32gui
import win32process
import ui.ui as ui
import process


def is_elden_ring_focused():
    foreground_window = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(foreground_window)
    return pid == process.ER_EXE.process_id


def trigger_quitout():
    if is_elden_ring_focused():
        process.ER_EXE.write_uchar(process.QUITOUT_ADDRESS, 1)
        ui.notify("Quitout triggered")


def trigger_import_savestate():
    if is_elden_ring_focused():
        ui.show_import_savestate()


def trigger_administer_savestate():
    if is_elden_ring_focused():
        ui.administer_savestates()


def trigger_toggle_runarc():
    try:
        addr = process.get_rune_arc_address()
        current = process.ER_EXE.read_uchar(addr)
        process.ER_EXE.write_uchar(addr, 0 if current else 1)
        ui.notify(f"Rune Arc {'ON' if not current else 'OFF'}")
    except Exception:
        # not in game
        pass
