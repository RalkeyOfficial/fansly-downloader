import concurrent.futures
import io

import av
import m3u8
from typing import Dict, TypedDict
from rich.table import Column
from rich.progress import Progress, BarColumn, TextColumn


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


class M3U8:
    def __init__(self, headers, session):
        self.headers = headers
        self.session = session

    def download(self, m3u8_url: str, save_path: str) -> TDownloadResult:
        # parse m3u8_url for required strings
        parsed_url = {k: v for k, v in [s.split('=') for s in m3u8_url.split('?')[-1].split('&')]}

        m3u8_url = m3u8_url.split('?')[0]  # re-construct original .m3u8 base link
        split_m3u8_url = m3u8_url.rsplit('/', 1)[0]  # used for constructing .ts chunk links
        save_path = save_path.rsplit('.m3u8')[0]  # remove file_extension from save_path

        cookies = get_cookies(parsed_url)

        # download the m3u8 playlist
        playlist_content_req = self.session.get(m3u8_url, headers=self.headers, cookies=cookies)
        if not playlist_content_req.ok:
            return {
                'status': 1,
                'message': f'Failed downloading m3u8; at playlist_content request. Response code: {playlist_content_req.status_code}\n{playlist_content_req.text}'
            }

        try:
            # parse the m3u8 playlist content using the m3u8 library
            playlist_obj = m3u8.loads(playlist_content_req.text)

            # get a list of all the .ts files in the playlist
            ts_files = [segment.uri for segment in playlist_obj.segments if segment.uri.endswith('.ts')]
        except Exception as e:
            return {
                'status': 1,
                'message': f'Failed getting TS uri\'s; at m3u8.loads(playlist_content_req.text), ts_files = [...]. Error message:\n{e}'
            }

        # define a nested function to download a single .ts file and return the content
        def download_ts(ts_file: str):
            ts_url = f"{split_m3u8_url}/{ts_file}"
            ts_response = self.session.get(ts_url, headers=self.headers, cookies=cookies, stream=True)
            buffer = io.BytesIO()
            for chunk in ts_response.iter_content(chunk_size=1024):
                buffer.write(chunk)
            ts_content = buffer.getvalue()
            return ts_content

        # if m3u8 seems like it might be bigger in total file size; display loading bar
        text_column = TextColumn(f"", table_column=Column(ratio=0.355))
        bar_column = BarColumn(bar_width=60, table_column=Column(ratio=2))
        disable_loading_bar = False if len(ts_files) > 15 else True
        progress = Progress(text_column, bar_column, expand=True, transient=True, disable=disable_loading_bar)
        with progress:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                ts_contents = [file for file in
                               progress.track(executor.map(download_ts, ts_files), total=len(ts_files))]

        segment = bytearray()
        for ts_content in ts_contents:
            segment += ts_content

        # Attempted to fix the error when audio does not exist, i think i fixed it, not sure, since i dont understand this code
        input_container = av.open(io.BytesIO(segment), format='mpegts')
        video_stream = input_container.streams.video[0]
        audio_stream = input_container.streams.audio[0] if input_container.streams.audio else None

        # define output container and streams
        output_container = av.open(f"{save_path}.mp4", 'w')  # add .mp4 file extension
        video_stream = output_container.add_stream(template=video_stream)
        audio_stream = output_container.add_stream(template=audio_stream) if audio_stream else None

        start_pts = None
        for packet in input_container.demux():
            if packet.dts is None:
                continue

            if start_pts is None:
                start_pts = packet.pts

            packet.pts -= start_pts
            packet.dts -= start_pts

            if packet.stream == input_container.streams.video[0]:
                packet.stream = video_stream
            elif audio_stream and packet.stream == input_container.streams.audio[0]:
                packet.stream = audio_stream
            output_container.mux(packet)

        # close containers
        input_container.close()
        output_container.close()

        return {
            'status': 0,
            'message': 'Success',
        }
