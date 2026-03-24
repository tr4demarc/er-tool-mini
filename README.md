# ER Tool Mini

A minimal Elden Ring Practice Tool written in Python.

<img width="415" height="223" alt="ER Tool mini" src="image.png" />

Includes save state manager, fast quitout, and rune arc toggle.

On the load save state screen use PgUp / PgDown to move save states.

Will only work on Windows. Use this only offline / with EAC disabled. See https://www.nexusmods.com/eldenring/mods/90.

## How to run using binary

1. Start Elden Ring
2. Run `ER-Tool-mini.exe`

## Run using Python

1. Start Elden Ring
2. Open Terminal

```
python main.py
```

If you run into issues:

```
> python -m venv venv
> venv\Scripts\activate
> pip install -r requirements.txt
> python main.py
```
