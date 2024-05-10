import os
import platform
import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, TypedDict

from ffmpeg import FFmpeg


class TDownloadResult(TypedDict):
    status: int
    message: str


def get_cookies(parsed_url: dict) -> Dict[str, str]:
    return {
        'CloudFront-Key-Pair-Id': parsed_url.get('Key-Pair-Id'),
        'CloudFront-Signature': parsed_url.get('Signature'),
        'CloudFront-Policy': parsed_url.get('Policy'),
        'ngsw-bypass': 'true'
    }


class MPD:
    def __init__(self, headers, session):
        self.headers = headers
        self.session = session

    def download(self, mpd_url: str, save_path: str) -> TDownloadResult:
        # parse mpd_url for required strings
        parsed_url = {k: v for k, v in [s.split('=') for s in mpd_url.split('?')[-1].split('&')]}

        save_path = save_path.rsplit('.mpd')[0] + ".mp4"  # remove file_extension from save_path

        headers = self.headers
        cookies = get_cookies(parsed_url)

        # Send a GET request to the MPD URL
        playlist_content = self.session.get(mpd_url, headers=headers, cookies=cookies)
        if not playlist_content.ok:
            return {
                'status': 1,
                'message': f'Failed downloading mpd; at playlist_content request. Response code: {playlist_content.status_code}\n{playlist_content.text}'
            }

        # Parse the MPD XML file
        root = ET.fromstring(playlist_content.content)

        # Find the highest quality video and audio representations
        video_representations = root.findall('.//{urn:mpeg:dash:schema:mpd:2011}AdaptationSet[@mimeType="video/mp4"]/{urn:mpeg:dash:schema:mpd:2011}Representation')
        audio_representations = root.findall('.//{urn:mpeg:dash:schema:mpd:2011}AdaptationSet[@mimeType="audio/mp4"]/{urn:mpeg:dash:schema:mpd:2011}Representation')

        highest_quality_video = max(video_representations, key=lambda x: int(x.attrib['bandwidth']))
        # check if audio exists before passing it along since it can lack audio
        highest_quality_audio = max(audio_representations, key=lambda x: int(x.attrib['bandwidth'])) if audio_representations else None

        # Extract the BaseURLs from the highest quality video and audio representations
        video_base_url = highest_quality_video.find('{urn:mpeg:dash:schema:mpd:2011}BaseURL').text
        audio_base_url = highest_quality_audio.find('{urn:mpeg:dash:schema:mpd:2011}BaseURL').text if highest_quality_audio else None

        # Construct the full URLs for the video and audio files
        base_url = '/'.join(mpd_url.split('/')[:-1]) + '/'
        video_url = base_url + video_base_url
        audio_url = base_url + audio_base_url if audio_base_url else None

        # Create a hidden temp folder to store downloads in
        hidden_folder_dir = ".temp"
        os_name = platform.system()
        if os_name == 'Windows':
            # Create the folder if it doesn't exist
            if not os.path.exists(hidden_folder_dir):
                os.mkdir(hidden_folder_dir)

            # Set the folder's hidden attribute in Windows
            subprocess.run(['attrib', '+h', hidden_folder_dir], check=True)
        else:
            if not os.path.exists(hidden_folder_dir):
                os.mkdir(hidden_folder_dir)

        def download_file(url, file_path):
            if url is None:
                return
            res = self.session.get(url, headers=headers, cookies=cookies, stream=True)
            res.raise_for_status()  # Raise an exception if the request fails
            with open(file_path, 'wb') as f:
                for chunk in res.iter_content(chunk_size=1024):
                    f.write(chunk)

        # hidden temp folder + file names
        video_file_path = os.path.join(hidden_folder_dir, "temp_video.mp4")
        audio_file_path = os.path.join(hidden_folder_dir, "temp_audio.mp4")

        # start download of the video and audio, and put it in the hidden folder
        download_file(video_url, video_file_path)
        download_file(audio_url, audio_file_path)

        # combine the video and audio together into 1 file IF both video and audio are present
        if video_url and audio_url:
            # I am aware that using FFMPEG is not the best practice, however I don't know of any better alternative
            ffmpeg = (
                FFmpeg()
                .option("y")
                .input(video_file_path)
                .input(audio_file_path)
                .output(
                    save_path,
                    codec="copy",
                )
            )
            ffmpeg.execute()
        elif video_url and not audio_url:  # else move the video in .temp folder to the normal path + rename it
            os.rename(video_file_path, save_path)

        # remove the video and audio file in the temp folder after everything is done
        try:  # if there is not a video file at video_file_path, continue the code without giving error
            os.remove(video_file_path)
        except OSError:
            pass

        try:  # if there is not a audio file at audio_file_path, continue the code without giving error
            os.remove(audio_file_path)
        except OSError:
            pass

        return {
            'status': 0,
            'message': 'Success',
        }
