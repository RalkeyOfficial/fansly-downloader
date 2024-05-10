import configparser
import sys
from os.path import join
from os import getcwd
from pathlib import Path

from utils.config.fanslyconfig import FanslyConfig
from utils.enums import LOGLEVEL, DownloadMode, MetadataHandling
from utils.errors import ConfigError
from utils.logger import output
from utils.open_url import open_url
from utils.update_util import apply_old_config_values, delete_deprecated_files, check_latest_release


def sanitize_creator_name(name: str) -> str:
    """
    Sanitizes a list of creator names after they have been
    parsed from a configuration file.

    This will:

    * remove empty names
    * remove leading/trailing whitespace from a name
    * remove a leading @ from a name
    * lower-case each name (for de-duplication to work)

    :param str name: A list of names to process.

    :return: A set of unique, sanitized creator names.
    :rtype: str
    """
    return name.strip().removeprefix('@').lower() if name.strip() else ''


def load_config(config: FanslyConfig):
    output(LOGLEVEL.INFO, 'Reading config.ini file ...')

    # create config path
    config.config_path = Path(join(getcwd(), 'config.ini'))

    if not config.config_path.exists():
        output(LOGLEVEL.ERROR, f"config.ini file not found or can not be read.\n{21 * ' '}Please download it & make sure it is in the same directory as fansly downloader")
        input('\nPress Enter to close ...')
        exit()

    config.load_raw_config()

    try:
        # TargetedCreator
        if config.username is None:
            user_names = config.parser.get('TargetedCreator', 'Username', fallback="ReplaceMe")  # string
            config.username = sanitize_creator_name(user_names)

        # MyAccount
        config.token = config.parser.get('MyAccount', 'Authorization_Token', fallback="ReplaceMe")  # string
        config.user_agent = config.parser.get('MyAccount', 'User_Agent', fallback="ReplaceMe")  # string

        # Options
        # Normal (Timeline & Messages), Timeline, Messages, Single (Single by post id) or Collections -> str
        download_mode = config.parser.get('Options', 'download_mode', fallback='Normal')
        config.download_mode = DownloadMode(download_mode.upper())
        config.show_downloads = config.parser.getboolean('Options', 'show_downloads', fallback=True)
        config.download_media_previews = config.parser.getboolean('Options', 'download_media_previews', allback=True)
        config.open_folder_when_finished = config.parser.getboolean('Options', 'open_folder_when_finished', fallback=True)

        # Local_directory, C:\MyCustomFolderFilePath -> str
        config.download_directory = Path(
            config.parser.get('Options', 'download_directory', fallback='Local_directory')
        )

        config.separate_messages = config.parser.getboolean('Options', 'separate_messages', fallback=True)
        config.separate_previews = config.parser.getboolean('Options', 'separate_previews', fallback=False)
        config.separate_timeline = config.parser.getboolean('Options', 'separate_timeline', fallback=True)
        config.use_duplicate_threshold = config.parser.getboolean('Options', 'use_duplicate_threshold', fallback=False)
        # Advanced, Simple -> str
        metadata_handling = config.parser.get('Options', 'metadata_handling', fallback='Advanced')
        config.metadata_handling = MetadataHandling(metadata_handling.upper())

    except configparser.NoOptionError as e:
        error_string = str(e)
        output(LOGLEVEL.ERROR, f"Your config.ini file is invalid, please download a fresh version of it from GitHub.\n{error_string}")
        input('\nPress Enter to close ...')
        exit()
    except ValueError as e:
        error_string = str(e)

        if 'a boolean' in error_string:
            output(LOGLEVEL.ERROR, f"""'{error_string.rsplit('boolean: ')[1]}' is malformed in the configuration file! This value can only be True or False
                                            {17 * ' '}Read the Wiki > Explanation of provided programs & their functionality > config.ini [1]""")
            open_url('https://github.com/RalkeyOfficial/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#explanation-of-configini')
        else:
            output(LOGLEVEL.ERROR, f"""You have entered a wrong value in the config.ini file -> '{error_string}'
                                            {17 * ' '}Read the Wiki > Explanation of provided programs & their functionality > config.ini [2]""")
            open_url('https://github.com/RalkeyOfficial/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#explanation-of-configini')

        input('\nPress Enter to close ...')
        exit()
    except (KeyError, NameError) as key:
        output(LOGLEVEL.ERROR, f"""'{key}' is missing or malformed in the configuration file!
                                        {17 * ' '}Read the Wiki > Explanation of provided programs & their functionality > config.ini [3]""")
        open_url('https://github.com/RalkeyOfficial/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#explanation-of-configini')

        input('\nPress Enter to close ...')
        exit()

    # starting here: self updating functionality
    # if started with --update start argument
    if len(sys.argv) > 1 and sys.argv[1] == '--update':
        # get the version string of what we've just been updated to
        version_string = sys.argv[2]

        # check if old config.ini exists, compare each pre-existing value of it and apply it to new config.ini
        apply_old_config_values()

        # temporary: delete deprecated files
        delete_deprecated_files()

        # get release description and if existent; display it in terminal
        check_latest_release(update_version=version_string, intend='update')

        # read the config.ini file for a last time
        config.parser.read(config.config_path)
    else:
        # check if a new version is available
        check_latest_release(current_version=config.parser.get('Other', 'version'), intend='check')

    # read & verify config values
    try:
        # TargetedCreator
        config_username = config.parser.get('TargetedCreator', 'Username')  # string

        # MyAccount
        config_token = config.parser.get('MyAccount', 'Authorization_Token')  # string
        config_useragent = config.parser.get('MyAccount', 'User_Agent')  # string

        # Options
        download_mode = config.parser.get('Options', 'download_mode').capitalize()  # Normal (Timeline & Messages), Timeline, Messages, Single (Single by post id) or Collections -> str
        show_downloads = config.parser.getboolean('Options', 'show_downloads')  # True, False -> boolean
        download_media_previews = config.parser.getboolean('Options', 'download_media_previews')  # True, False -> boolean
        open_folder_when_finished = config.parser.getboolean('Options', 'open_folder_when_finished')  # True, False -> boolean
        separate_messages = config.parser.getboolean('Options', 'separate_messages')  # True, False -> boolean
        separate_previews = config.parser.getboolean('Options', 'separate_previews')  # True, False -> boolean
        separate_timeline = config.parser.getboolean('Options', 'separate_timeline')  # True, False -> boolean
        utilise_duplicate_threshold = config.parser.getboolean('Options', 'utilise_duplicate_threshold')  # True, False -> boolean
        download_directory = config.parser.get('Options', 'download_directory')  # Local_directory, C:\MyCustomFolderFilePath -> str
        metadata_handling = config.parser.get('Options', 'metadata_handling').capitalize()  # Advanced, Simple -> str

        # Other
        current_version = config.get('Other', 'version')  # str
    except configparser.NoOptionError as e:
        error_string = str(e)
        output(LOGLEVEL.ERROR, f"Your config.ini file is very malformed, please download a fresh version of it from GitHub.\n{error_string}")
        input('\nPress Enter to close ...')
        exit()
    except ValueError as e:
        error_string = str(e)
        if 'a boolean' in error_string:
            output(LOGLEVEL.ERROR, f"""\'{error_string.rsplit('boolean: ')[1]}\' is malformed in the configuration file! This value can only be True or False
                                            {6 * ' '}Read the Wiki > Explanation of provided programs & their functionality > config.ini""", 1)
            open_url('https://github.com/RalkeyOfficial/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#explanation-of-configini')
            input('\nPress Enter to close ...')
            exit()
        else:
            output(LOGLEVEL.ERROR, f"""You have entered a wrong value in the config.ini file -> '{error_string}'
                                            {6 * ' '}Read the Wiki > Explanation of provided programs & their functionality > config.ini""", 2)
            open_url('https://github.com/RalkeyOfficial/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#explanation-of-configini')
            input('\nPress Enter to close ...')
            exit()
    except (KeyError, NameError) as key:
        output(LOGLEVEL.ERROR, f"""\'{key}\' is missing or malformed in the configuration file!
                                        {6 * ' '}Read the Wiki > Explanation of provided programs & their functionality > config.ini""", 3)
        open_url('https://github.com/RalkeyOfficial/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#explanation-of-configini')
        input('\nPress Enter to close ...')
        exit()


def save_config_or_raise(config: FanslyConfig) -> bool:
    if not config.save_config():
        raise ConfigError(
            f"Internal error: Configuration data could not be saved to '{config.config_path}'. "
            "Invalid path or permission/security software problem."
        )
    else:
        return True
