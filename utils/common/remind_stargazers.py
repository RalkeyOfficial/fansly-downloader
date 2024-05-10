import requests

from time import sleep as s
from utils.enums import LOGLEVEL
from utils.logger import output


def remind_stargazing(__version__: str) -> bool:
    stargazers_count, total_downloads = 0, 0

    # depends on global variable current_version
    stats_headers = {'user-agent': f"Avnsx/Fansly Downloader {__version__}",
                     'referer': f"Avnsx/Fansly Downloader {__version__}",
                     'accept-language': 'en-US,en;q=0.9'}

    # get total_downloads count
    stargazers_check_request = requests.get('https://api.github.com/repos/RalkeyOfficial/fansly-downloader/releases',
                                            allow_redirects=True, headers=stats_headers)
    if not stargazers_check_request.ok:
        return False
    stargazers_check_request = stargazers_check_request.json()
    for x in stargazers_check_request:
        total_downloads += x['assets'][0]['download_count'] or 0

    # get stargazers_count
    downloads_check_request = requests.get('https://api.github.com/repos/RalkeyOfficial/fansly-downloader',
                                           allow_redirects=True, headers=stats_headers)
    if not downloads_check_request.ok:
        return False
    downloads_check_request = downloads_check_request.json()
    stargazers_count = downloads_check_request['stargazers_count'] or 0

    percentual_stars = round(stargazers_count / total_downloads * 100, 2)

    # display message (intentionally "lnfo" with lvl 4)
    output(LOGLEVEL.INFO_IMPORTANT,
           f"""Fansly Downloader was downloaded {total_downloads} times, but only {percentual_stars} % of You(!) have starred it.
                                        {6 * ' '}Stars directly influence my willingness to continue maintaining the project.\n\
                                        {5 * ' '}Help the repository grow today, by leaving a star on it and sharing it to others online!""")
    s(10)
