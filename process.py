import pymem
import win32gui
import win32process
import pymem.process


ER_EXE: pymem.Pymem
_module = None

QUITOUT_ADDRESS: int
ELDEN_RING_HWND: int
WORLD_CHR_MAN_OFF: int
WORLD_CHR_MAN_PLAYER_OFF2: int
PG_DATA_OFFSET: int


def init():
    global ER_EXE, _module, QUITOUT_ADDRESS, ELDEN_RING_HWND
    global WORLD_CHR_MAN_OFF, WORLD_CHR_MAN_PLAYER_OFF2, PG_DATA_OFFSET

    ER_EXE = pymem.Pymem("eldenring.exe")
    _module = pymem.process.module_from_name(ER_EXE.process_handle, "eldenring.exe")
    QUITOUT_ADDRESS = get_quitout_addr()
    ELDEN_RING_HWND = get_elden_ring_hwnd()

    # Cache rune arc offsets to avoid re-scanning the module every time
    # Can't get the full address upfront because it fails if user is on the load screen
    WORLD_CHR_MAN_OFF, WORLD_CHR_MAN_PLAYER_OFF2, PG_DATA_OFFSET = (
        get_rune_arc_offsets()
    )


def get_elden_ring_hwnd() -> int:
    result = []

    def callback(hwnd, _):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid == ER_EXE.process_id:
            result.append(hwnd)

    win32gui.EnumWindows(callback, None)
    if not result:
        raise RuntimeError("Could not find Elden Ring window")
    return result[0]


def find_aob(pattern: list[int | None], start_offset=0, end_offset=None):
    """Scan process memory for an array-of-bytes pattern. None = wildcard."""
    global _module
    if _module:
        base = _module.lpBaseOfDll
        size = _module.SizeOfImage
    else:
        raise RuntimeError("Could not find eldenring.exe module")
    data = ER_EXE.read_bytes(base + start_offset, (end_offset or size) - start_offset)
    for i in range(len(data) - len(pattern)):
        if all(p is None or data[i + j] == p for j, p in enumerate(pattern)):
            return base + start_offset + i
    raise RuntimeError("Could not find pattern in memory")


def get_quitout_addr() -> int:
    # Quitout address is at CS::GameMan (game manager) + 0x10,
    # and CS::GameMan is found by the following pattern:
    game_man_pattern = [
        0x48,
        0x8B,
        0x05,
        None,  # Relative offset byte 1
        None,  # Relative offset byte 2
        None,  # Relative offset byte 3
        None,  # Relative offset byte 4
        0x0F,
        0xB6,
        0x40,
        0x10,
        0xC3,
    ]
    # Find beginning of game_man_pattern and read the relative offset
    # to get the address of CS::GameMan, then read the pointer and
    # add 0x10 to get quitout address
    game_man_instr_addr = find_aob(game_man_pattern, start_offset=6_500_000)
    rel_offset = ER_EXE.read_int(game_man_instr_addr + 3)
    game_man_ptr_addr = game_man_instr_addr + 7 + rel_offset
    game_man_address = int(ER_EXE.read_longlong(game_man_ptr_addr))
    return game_man_address + 0x10


def get_rune_arc_offsets() -> tuple[int, int, int]:
    """AOB scan to recover the stable offsets needed to locate the rune arc flag."""
    global _module
    if _module:
        base = _module.lpBaseOfDll
    else:
        raise RuntimeError("Could not find eldenring.exe module")

    world_chr_man_pattern = [
        0xE8,
        None,
        None,
        None,
        None,
        0x48,
        0x8B,
        0x05,
        None,
        None,
        None,
        None,
        0x4C,
        0x8B,
        0xA8,
        None,
        None,
        None,
        None,
        0x4D,
        0x85,
        0xED,
        0x0F,
        0x84,
        None,
        None,
        None,
        None,
    ]
    world_chr_man_instr_addr = find_aob(world_chr_man_pattern, start_offset=1_800_000)
    rel_to_world_chr = ER_EXE.read_int(world_chr_man_instr_addr + 8)
    world_chr_ptr_addr = world_chr_man_instr_addr + 12 + rel_to_world_chr
    world_chr_man_off = world_chr_ptr_addr - base
    world_chr_man_player_off2 = ER_EXE.read_int(world_chr_man_instr_addr + 15)

    pg_data_pattern = [
        0x48,
        0x8B,
        0x81,
        None,
        None,
        0x00,
        0x00,
        0x48,
        0xC7,
        0x02,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0x48,
        0x85,
        0xC0,
        0x74,
        0x0A,
        0x48,
        0x8B,
        0x80,
        None,
        None,
        0x00,
        0x00,
        0x48,
        0x89,
        0x02,
        0x48,
        0x8B,
        0xC2,
    ]
    pg_data_instr_addr = find_aob(pg_data_pattern, start_offset=6_400_000)
    pg_data_offset = ER_EXE.read_int(pg_data_instr_addr + 3)

    return int(world_chr_man_off), int(world_chr_man_player_off2), int(pg_data_offset)


def get_rune_arc_address() -> int:
    """Follow the pointer chain to the rune arc flag. Must be called while in game."""
    global _module
    if _module:
        base = _module.lpBaseOfDll
    else:
        raise RuntimeError("Could not find eldenring.exe module")

    world_chr_man = int(ER_EXE.read_longlong(base + WORLD_CHR_MAN_OFF))
    player_ins = int(ER_EXE.read_longlong(world_chr_man + WORLD_CHR_MAN_PLAYER_OFF2))
    pg_data = int(ER_EXE.read_longlong(player_ins + PG_DATA_OFFSET))
    return pg_data + 0xFF
