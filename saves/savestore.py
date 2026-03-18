import os
from glob import glob


def _get_er_saves_base_path() -> str:
    """Get the path where the saves are stored.

    The path will be `/%%appdata%%/EldenRing/{Steam ID}/`"""
    base_path = glob(os.path.expandvars("%appdata%\\EldenRing\\*\\"))
    if not base_path:
        raise RuntimeError("Could not find Elden Ring saves directory")
    return base_path[0]


def _get_savefile_path() -> str:
    """Get the path to the save file.

    The path will be `%%appdata%%/EldenRing/{Steam ID}/ER0000.sl2`"""
    path = os.path.join(_ER_SAVES_BASE_PATH, SAVEFILE_NAME)
    if not path:
        raise RuntimeError("Could not find Elden Ring save file")
    return path


def _get_savestore_path() -> str:
    """Get the path to this app's savestore directory.

    The path will be `%%appdata%%/EldenRing/{Steam ID}/savestore/`"""
    path = os.path.join(_ER_SAVES_BASE_PATH, "savestore")
    return path


def _get_file_order_path() -> str:
    """Get the path to the file that stores the order of this app's savestates.

    The file will be `%%appdata%%/EldenRing/{Steam ID}/savestore/file_order.txt`"""
    return os.path.join(SAVESTORE_PATH, "file_order.txt")


_ER_SAVES_BASE_PATH = _get_er_saves_base_path()

SAVEFILE_NAME = "ER0000.sl2"
SAVEFILE_PATH = _get_savefile_path()
SAVESTORE_PATH = _get_savestore_path()
FILE_ORDER_PATH = _get_file_order_path()
