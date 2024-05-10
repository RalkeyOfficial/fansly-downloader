import platform
import re
import traceback

from utils.enums import LOGLEVEL
from utils.logger import output


def guess_user_agent(user_agents: dict, based_on_browser: str, default_ua: str) -> str:
    """Returns the guessed browser's user agent or a default one."""

    if based_on_browser == 'Microsoft Edge':
        based_on_browser = 'Edg'  # msedge only reports "Edg" as its identifier

        # could do the same for opera, opera gx, brave. but those are not supported by @jnrbsn's repo. so we just return chrome ua
        # in general his repo, does not provide the most accurate latest user-agents, if I am borred some time in the future,
        # I might just write my own similar repo and use that instead

    os_name = platform.system()

    try:
        if os_name == "Windows":
            for user_agent in user_agents:
                if based_on_browser in user_agent and "Windows" in user_agent:
                    match = re.search(r'Windows NT ([\d.]+)', user_agent)
                    if match:
                        os_version = match.group(1)
                        if os_version in user_agent:
                            return user_agent

        elif os_name == "Darwin":  # macOS
            for user_agent in user_agents:
                if based_on_browser in user_agent and "Macintosh" in user_agent:
                    match = re.search(r'Mac OS X ([\d_.]+)', user_agent)
                    if match:
                        os_version = match.group(1).replace('_', '.')
                        if os_version in user_agent:
                            return user_agent

        elif os_name == "Linux":
            for user_agent in user_agents:
                if based_on_browser in user_agent and "Linux" in user_agent:
                    match = re.search(r'Linux ([\d.]+)', user_agent)
                    if match:
                        os_version = match.group(1)
                        if os_version in user_agent:
                            return user_agent

    except Exception:
        output(LOGLEVEL.ERROR, f'Regexing user-agent from online source failed: {traceback.format_exc()}', 4)

    output(LOGLEVEL.WARNING, f"Missing user-agent for {based_on_browser} & OS: {os_name}. Chrome & Windows UA will be used instead.")

    return default_ua
