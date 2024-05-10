from enum import Enum, auto, StrEnum


class LOGLEVEL(Enum):
    INFO = auto()
    INFO_IMPORTANT = auto()
    UPDATE = auto()
    CONFIG = auto()
    WARNING = auto()
    ERROR = auto()


class DownloadMode(StrEnum):
    NOTSET = auto()
    NORMAL = auto()
    TIMELINE = auto()
    COLLECTION = auto()
    SINGLE = auto()
    MESSAGES = auto()


class MetadataHandling(StrEnum):
    NOTSET = auto()
    ADVANCED = auto()
    SIMPLE = auto()
