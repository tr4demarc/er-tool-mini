import keyboard
import process
import triggers


def main():

    print(
        "==========ER Tool mini==========\n"
        "Listening.\n"
        "- Ctrl+S to import savestate\n"
        "- . to load savestate\n"
        "- P to trigger quitout\n"
        "- O to toggle rune arc\n"
        "Press Ctrl+C to exit."
    )

    keyboard.add_hotkey("P", triggers.trigger_quitout)
    keyboard.add_hotkey("Ctrl+S", triggers.trigger_import_savestate)
    keyboard.add_hotkey(".", triggers.trigger_administer_savestate)
    keyboard.add_hotkey("O", triggers.trigger_toggle_runarc)

    keyboard.wait()


if __name__ == "__main__":
    try:
        process.init()
        main()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit")
