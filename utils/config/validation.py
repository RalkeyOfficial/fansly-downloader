import re
import requests

from pathlib import Path
from time import sleep
from requests.exceptions import RequestException

from .config import save_config_or_raise
from .fanslyconfig import FanslyConfig

from ..enums import LOGLEVEL
from ..errors import ConfigError
from ..logger import output
from ..open_url import open_url
from ..path import ask_correct_dir
from ..web import guess_user_agent


def validate_adjust_creator_name(config: FanslyConfig) -> bool:
    def username_has_valid_chars(name: str) -> bool:
        if name is None:
            return False
        return bool(re.match(r"^([a-zA-Z0-9-_]*)$", name))

    def validate_creator_name(name: str) -> bool:
        name = name.strip().removeprefix('@')
        user_base_text = f"Invalid targeted creator name '@{name}':"
        user_error = False

        if 'ReplaceMe'.lower() in name.lower():
            output(LOGLEVEL.WARNING, f"Config.ini value '{name}' for TargetedCreator > Username is a placeholder value.")
            user_error = True
        if ' ' in name:
            output(LOGLEVEL.WARNING, f'{user_base_text} name must not contain spaces.')
            user_error = True
        if not (4 <= len(name) <= 30):
            output(LOGLEVEL.WARNING, f"{user_base_text} must be between 4 and 30 characters long!\n")
            user_error = True
        if not username_has_valid_chars(name):
            output(LOGLEVEL.WARNING, f"{user_base_text} should only contain\n{20 * ' '}alphanumeric characters, hyphens, or underscores!\n")
            user_error = True

        return user_error

    def get_input_username() -> str:
        output(LOGLEVEL.INFO, f"""Enter the username handle (eg. @MyCreatorsName or MyCreatorsName)
                                 {19 * ' '}of the Fansly creator you want to download content from.""")

        input_name = input(f"\n{19 * ' '}► Enter a valid username: ")

        if validate_creator_name(input_name):
            return input_name.strip().removeprefix('@')
        else:
            return get_input_username()

    if (config.username is None) or not validate_creator_name(config.username):
        _name = get_input_username()

        config.parser.set('TargetedCreator', 'username', _name)
        config.save_config()

    return True


def validate_adjust_token(config: FanslyConfig) -> None:
    plyvel_installed, browser_name = False, None

    if not config.token_is_valid():
        try:
            import plyvel
            plyvel_installed = True

        except ImportError:
            output(LOGLEVEL.WARNING, f"""Fansly Downloader's automatic configuration for the authorization_token in the config.ini file will be skipped.
                                    {20*' '}Your system is missing required plyvel (python module) builds by Siyao Chen (@liviaerxin).
                                    {20*' '}Installable with 'pip3 install plyvel-ci' or from github.com/liviaerxin/plyvel/releases/latest""")

    # semi-automatically set up value for config_token (authorization_token) based on the users input
    if plyvel_installed and not config.token_is_valid():
        # fansly-downloader plyvel dependant package imports
        from utils.config_util import (
            get_browser_paths,
            parse_browser_from_string,
            find_leveldb_folders,
            get_auth_token_from_leveldb_folder,
            process_storage_folders,
            link_fansly_downloader_to_account
        )

        output(LOGLEVEL.WARNING,
            f"Authorization token '{config.token}' is unmodified, missing or malformed"
            f"\n{20 * ' '}in the configuration file.")

        output(LOGLEVEL.CONFIG,
            f"Trying to automatically configure Fansly authorization token"
            f"\n{19 * ' '}from any browser storage available on the local system ...")

        browser_paths = get_browser_paths()
        processed_account = None

        for path in browser_paths:
            processed_token = None

            # if not firefox, process leveldb folders
            if 'firefox' not in path.lower():
                leveldb_folders = find_leveldb_folders(path)
                for folder in leveldb_folders:
                    processed_token = get_auth_token_from_leveldb_folder(folder)
                    if processed_token:
                        processed_account = link_fansly_downloader_to_account(processed_token)
                        break  # exit the inner loop if a valid processed_token is found

            # if firefox, process sqlite db instead
            else:
                processed_token = process_storage_folders(path)
                if processed_token:
                    processed_account = link_fansly_downloader_to_account(processed_token)

            if all([processed_account, processed_token]):
                processed_from_path = parse_browser_from_string(path)  # we might also utilise this for guessing the useragent

                # let user pick a account, to connect to fansly downloader
                output(LOGLEVEL.CONFIG, f"Do you want to link the account \'{processed_account}\' to Fansly Downloader? (found in: {processed_from_path})")

                while True:
                    user_input_acc_verify = input(f"{20 * ' '}► Type either 'Yes' or 'No': ").strip().lower()
                    if user_input_acc_verify == "yes" or user_input_acc_verify == "no":
                        break  # break user input verification
                    else:
                        output(LOGLEVEL.ERROR, f"Please enter either 'Yes' or 'No', to decide if you want to link to \'{processed_account}\'")

                # based on user input; write account username & auth token to config.ini
                if user_input_acc_verify == "yes" and all([processed_account, processed_token]):
                    config.token = processed_token
                    config.token_from_browser_name = processed_from_path

                    save_config_or_raise(config)

                    output(LOGLEVEL.INFO, f"Success! Authorization token applied to config.ini file\n")
                    break  # break whole loop

        # if no account auth, was found in any of the users browsers
        if not processed_account:
            open_url('https://github.com/RalkeyOfficial/fansly-downloader/wiki/Get-Started')

            raise ConfigError(
                f"Your Fansly account was not found in any of your browser's local storage."
                f"\n{18 * ' '}Did you recently browse Fansly with an authenticated session?"
                f"\n{18 * ' '}Please read & apply the 'Get-Started' tutorial."
            )

    # if users decisions have led to auth token still being invalid
    elif any([not config.token, 'ReplaceMe' in config.token]) or config.token and len(config.token) < 50:
        open_url('https://github.com/RalkeyOfficial/fansly-downloader/wiki/Get-Started')

        raise ConfigError(
            f"Reached the end and the authorization token in config.ini file is still invalid!"
            f"\n{18 * ' '}Please read & apply the 'Get-Started' tutorial."
        )


def validate_adjust_user_agent(config: FanslyConfig) -> None:
    ua_if_failed = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'

    based_on_browser = config.token_from_browser_name or 'Chrome'

    if not config.useragent_is_valid():
        output(LOGLEVEL.WARNING, f"Browser user-agent '{config.user_agent}' in config.ini is most likely incorrect.")

        if config.token_from_browser_name is not None:
            output(LOGLEVEL.CONFIG,
                   f"""Adjusting it with an educated guess based on the combination of your
                        {19*' '}operating system & specific browser.""")

        else:
            output(LOGLEVEL.CONFIG,
                   f"""Adjusting it with an educated guess, hardcoded for Chrome browser."
                        {19*' '}If you're not using Chrome you might want to replace it in the config.ini file later on."
                        {19*' '}More information regarding this topic is on the Fansly Downloader NG Wiki.""")

        try:
            # thanks, Jonathan Robson (@jnrbsn) - for continuously providing these up-to-date user-agents
            user_agent_response = requests.get(
                'https://jnrbsn.github.io/user-agents/user-agents.json',
                headers={
                    'User-Agent': ua_if_failed,
                    'accept-language': 'en-US,en;q=0.9'
                }
            )

            if user_agent_response.status_code == 200:
                config_user_agent = guess_user_agent(
                    user_agent_response.json(),
                    based_on_browser,
                    default_ua=ua_if_failed
                )
            else:
                config_user_agent = ua_if_failed

        except RequestException:
            config_user_agent = ua_if_failed

        # save useragent modification to config file
        config.user_agent = config_user_agent

        save_config_or_raise(config)

        output(LOGLEVEL.INFO, f"Success! Applied a browser user-agent to config.ini file.\n")


def validate_adjust_download_directory(config: FanslyConfig) -> None:
    if 'local_dir' in str(config.download_directory).lower():

        config.download_directory = Path.cwd()

        output(LOGLEVEL.INFO, f"Acknowledging local download directory: '{config.download_directory}'")

    # if user specified a correct custom downloads path
    elif config.download_directory is not None and config.download_directory.is_dir():

        output(LOGLEVEL.INFO, f"Acknowledging custom basis download directory: '{config.download_directory}'")

    else:  # if their set directory, can't be found by the OS
        output(LOGLEVEL.WARNING,
            f"The custom base download directory file path '{config.download_directory}' seems to be invalid!"
            f"\n{20*' '}Please change it to a correct file path, for example: 'C:\\MyFanslyDownloads'"
            f"\n{20*' '}An Explorer window to help you set the correct path will open soon!"
            f"\n{20*' '}You may right-click inside the Explorer to create a new folder."
            f"\n{20*' '}Select a folder and it will be used as the default download directory.")

        sleep(10)  # give user time to realise instructions were given

        config.download_directory = ask_correct_dir()  # ask user to select correct path using tkinters explorer dialog

        # save the config permanently into config.ini
        save_config_or_raise(config)


def validate_adjust_config(config: FanslyConfig) -> None:
    if not validate_adjust_creator_name(config):
        raise ConfigError('Configuration error - no valid creator name specified.')

    validate_adjust_token(config)

    validate_adjust_user_agent(config)

    validate_adjust_download_directory(config)
