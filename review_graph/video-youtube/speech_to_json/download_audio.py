import os
from urllib.parse import urlparse, parse_qs
import yt_dlp

def extract_video_id(url):
    query = urlparse(url).query
    return parse_qs(query).get("v", [None])[0]

def download_audio(video_url, video_id, audio_dir, ffmpeg_dir):
    output_path = os.path.join(audio_dir, f"{video_id}.%(ext)s")
    final_audio_path = os.path.join(audio_dir, f"{video_id}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'ffmpeg_location': ffmpeg_dir,
        'skip_download': False,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)

    video_title = info.get("title", "unknown_title")
    uploader = info.get("uploader", "unknown_author")
    upload_date = info.get("upload_date", "")  # dạng YYYYMMDD

    formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}" if upload_date else "unknown_date"

    return final_audio_path, video_title, uploader, formatted_date
