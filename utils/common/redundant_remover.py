# delete previous redundant pyinstaller folders, older then an hour
import os
import sys
import time


def del_redudant_pyinstaller_files():
    try:
        base_path = sys._MEIPASS
    except Exception:
        return

    temp_dir = os.path.abspath(os.path.join(base_path, '..'))
    current_time = time.time()

    for folder in os.listdir(temp_dir):
        try:
            item = os.path.join(temp_dir, folder)
            if folder.startswith('_MEI') and os.path.isdir(item) and (current_time - os.path.getctime(item)) > 3600:
                for root, dirs, files in os.walk(item, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(item)
        except Exception:
            pass