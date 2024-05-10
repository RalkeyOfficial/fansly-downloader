EXIT_SUCCESS: int = 0
EXIT_ERROR: int = -1
EXIT_ABORT: int = -2
UNEXPECTED_ERROR: int = -3
API_ERROR: int = -4
CONFIG_ERROR: int = -5
DOWNLOAD_ERROR: int = -6
SOME_USERS_FAILED: int = -7
UPDATE_FAILED: int = -10
UPDATE_MANUALLY: int = -11
UPDATE_SUCCESS: int = 1


class DuplicateCountError(RuntimeError):
    def __init__(self, duplicate_count):
        self.duplicate_count = duplicate_count
        self.message = f"Irrationally high rise in duplicates: {duplicate_count}"
        super().__init__(self.message)


class ConfigError(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)


class ApiError(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)


class ApiAuthenticationError(ApiError):
    def __init__(self, *args):
        super().__init__(*args)


class ApiAccountInfoError(ApiError):
    def __init__(self, *args):
        super().__init__(*args)


class DownloadError(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)


class MediaError(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)


class M3U8Error(MediaError):
    def __init__(self, *args):
        super().__init__(*args)


class InvalidMP4Error(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)


__all__ = [
    'EXIT_ABORT',
    'EXIT_ERROR',
    'EXIT_SUCCESS',
    'API_ERROR',
    'CONFIG_ERROR',
    'DOWNLOAD_ERROR',
    'SOME_USERS_FAILED',
    'UNEXPECTED_ERROR',
    'UPDATE_FAILED',
    'UPDATE_MANUALLY',
    'UPDATE_SUCCESS',
    'ApiError',
    'ApiAccountInfoError',
    'ApiAuthenticationError',
    'ConfigError',
    'DownloadError',
    'DuplicateCountError',
    'MediaError',
    'M3U8Error',
    'InvalidMP4Error',
]
