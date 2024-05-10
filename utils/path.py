from pathlib import Path
from tkinter import Tk, filedialog

from utils.enums import LOGLEVEL
from utils.logger import output


# if the users custom provided filepath is invalid; a tkinter dialog will open during runtime, asking to adjust download path
def ask_correct_dir() -> Path:
    root = Tk()
    root.withdraw()

    while True:
        directory_name = filedialog.askdirectory()

        if Path(directory_name).is_dir():
            output(LOGLEVEL.INFO, f"Folder path chosen: {directory_name}")
            return Path(directory_name)

        output(LOGLEVEL.ERROR, f"You did not choose a valid folder. Please try again!", 5)
