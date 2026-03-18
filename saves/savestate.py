import shutil
import os

from saves.savestore import SAVEFILE_PATH, SAVESTORE_PATH, FILE_ORDER_PATH


def import_savestate(savestate_name: str):
    os.makedirs(SAVESTORE_PATH, exist_ok=True)
    shutil.copy(SAVEFILE_PATH, os.path.join(SAVESTORE_PATH, savestate_name))


def load_savestate(savestate_name: str):
    shutil.copy(os.path.join(SAVEFILE_PATH), SAVEFILE_PATH + ".bak")
    shutil.copy(os.path.join(SAVESTORE_PATH, savestate_name), SAVEFILE_PATH)


def delete_savestate(savestate_name: str):
    os.remove(os.path.join(SAVESTORE_PATH, savestate_name))


def rename_savestate(old_name: str, new_name: str):
    os.rename(
        os.path.join(SAVESTORE_PATH, old_name),
        os.path.join(SAVESTORE_PATH, new_name),
    )


def update_savestates_order(savestate_names: list[str]):
    with open(FILE_ORDER_PATH, "w") as f:
        f.write("\n".join(savestate_names))


def get_savestates() -> list[str]:
    def _get_savestate_created_time(filename):
        return os.path.getmtime(os.path.join(SAVESTORE_PATH, filename))

    if not os.path.exists(SAVESTORE_PATH):
        return []

    if not os.path.exists(FILE_ORDER_PATH):
        files = [f for f in os.listdir(SAVESTORE_PATH)]
        files.sort(key=_get_savestate_created_time)
        with open(FILE_ORDER_PATH, "w") as f:
            f.write("\n".join(files))

    with open(FILE_ORDER_PATH, "r") as f:
        savestates = [line.strip() for line in f if line.strip()]

    return savestates
