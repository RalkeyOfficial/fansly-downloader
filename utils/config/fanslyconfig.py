from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set, List

from utils.config.metadatahandling import MetadataHandling
from utils.config.modes import DownloadMode


@dataclass()
class FanslyConfig(object):
    # Mandatory property
    # This should be set to __version__ in the main script.
    program_version: str

    # Define base threshold (used for when modules don't provide vars)
    DUPLICATE_THRESHOLD: int = 50

    # Configuration file
    config_path: Optional[Path] = None

    # Misc
    token_from_browser_name: Optional[str] = None

    # Objects
    parser = ConfigParser(interpolation=None)

    # TargetedCreator > username
    username: Optional[str] = None

    # MyAccount
    token: Optional[str] = None
    user_agent: Optional[str] = None

    # Options
    # "Normal" | "Timeline" | "Messages" | "Single" | "Collection"
    download_mode: DownloadMode = DownloadMode.NORMAL
    show_downloads: bool = True
    download_media_previews: bool = True
    open_folder_when_finished: bool = True
    download_directory: (None | Path) = None
    separate_messages: bool = True
    separate_previews: bool = False
    separate_timeline: bool = True
    use_duplicate_threshold: bool = False
    # "Advanced" | "Simple"
    metadata_handling: MetadataHandling = MetadataHandling.ADVANCED

    # Number of retries to get a timeline
    timeline_retries: int = 1
    # Anti-rate-limiting delay in seconds
    timeline_delay_seconds: List[int, int] = (30, 60)

    def load_raw_config(self) -> list[str]:
        if self.config_path is None:
            return []

        else:
            return self.parser.read(self.config_path)

    def _sync_settings(self) -> None:
        self.parser.set('TargetedCreator', 'username', self.username)

        self.parser.set('MyAccount', 'authorization_token', self.token)
        self.parser.set('MyAccount', 'user_agent', self.user_agent)

        if self.download_directory is None:
            self.parser.set('Options', 'download_directory', 'Local_directory')
        else:
            self.parser.set('Options', 'download_directory', str(self.download_directory))

        self.parser.set('Options', 'download_mode', str(self.download_mode).capitalize())
        self.parser.set('Options', 'metadata_handling', str(self.metadata_handling).capitalize())

        # Booleans
        self.parser.set('Options', 'show_downloads', str(self.show_downloads))
        self.parser.set('Options', 'download_media_previews', str(self.download_media_previews))
        self.parser.set('Options', 'open_folder_when_finished', str(self.open_folder_when_finished))
        self.parser.set('Options', 'separate_messages', str(self.separate_messages))
        self.parser.set('Options', 'separate_previews', str(self.separate_previews))
        self.parser.set('Options', 'separate_timeline', str(self.separate_timeline))
        self.parser.set('Options', 'use_duplicate_threshold', str(self.use_duplicate_threshold))

    def save_config(self) -> bool:
        if self.config_path is None:
            return False

        else:
            self._sync_settings()

            with self.config_path.open('w', encoding='utf-8') as f:
                self.parser.write(f)
                return True

    def token_is_valid(self) -> bool:
        if self.token is None:
            return False

        return not any(
            [
                len(self.token) < 50,
                'ReplaceMe' in self.token,
            ]
        )

    def useragent_is_valid(self) -> bool:
        if self.user_agent is None:
            return False

        return not any(
            [
                len(self.user_agent) < 40,
                'ReplaceMe' in self.user_agent,
            ]
        )
