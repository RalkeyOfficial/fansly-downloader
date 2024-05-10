import sys
from typing import Optional

from loguru import logger as log
from functools import partialmethod
from utils.enums import LOGLEVEL


# most of the time, we utilize this to display colored output rather than logging or prints
def output(level: LOGLEVEL, message: str, error_index: Optional[int] = None):
    log_type: str = ''
    log_level: int = 0
    color: str = ''

    if level == LOGLEVEL.INFO:
        log_type = '\n Info'
        log_level = 20
        color = '<light-blue>'
    if level == LOGLEVEL.INFO_IMPORTANT:
        log_type = '\n Info'
        log_level = 20
        color = '<light-red>'
    elif level == LOGLEVEL.UPDATE:
        log_type = '\n Updater'
        log_level = 20
        color = '<light-green>'
    elif level == LOGLEVEL.CONFIG:
        log_type = '\n Config'
        log_level = 20
        color = '<light-magenta>'
    elif level == LOGLEVEL.WARNING:
        log_type = '\n WARNING'
        log_level = 30
        color = '<yellow>'
    elif level == LOGLEVEL.ERROR:
        log_type = f'\n [{error_index}]ERROR' if error_index else '\n ERROR'
        log_level = 40
        color = '<red>'

    try:
        log.level(log_type, no=log_level, color=color)
    except TypeError:
        pass # level failsafe
    log.__class__.type = partialmethod(log.__class__.log, log_type)
    log.remove()
    log.add(sys.stdout, format="<level>{level}</level> | <white>{time:HH:mm}</white> <level>|</level><light-white>| {message}</light-white>", level=log_type)
    log.type(message)
