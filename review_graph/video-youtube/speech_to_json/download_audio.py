import os
from urllib.parse import urlparse, parse_qs
import yt_dlp

def extract_video_id(url):
	"""
	Extracts the YouTube video ID from a given URL:
		- Parses the query string of the URL
		- Retrieves the value of the 'v' parameter, which represents the video ID
	Inputs:
		url (str): The full YouTube video URL
	Output:
		str or None: The video ID if found, otherwise None
	"""

	query = urlparse(url).query

	return parse_qs(query).get("v", [None])[0]

def download_audio(video_url, video_id, audio_dir, ffmpeg_dir):
	"""
	Downloads the audio from a YouTube video and converts it to MP3 format:
		- Uses yt_dlp to extract and download the best audio stream
		- Converts the audio to MP3 using FFmpeg
		- Retrieves metadata including title, uploader, and upload date
	Inputs:
		video_url (str): The full YouTube video URL
		video_id (str): The extracted video ID used for naming the output file
		audio_dir (str): Directory where the audio file will be saved
		ffmpeg_dir (str): Path to the FFmpeg executable
	Output:
		tuple: (final_audio_path, video_title, uploader, formatted_date)
			- final_audio_path (str): Path to the saved MP3 file
			- video_title (str): Title of the video
			- uploader (str): Name of the video uploader
			- formatted_date (str): Upload date in YYYY-MM-DD format
	"""

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
	upload_date = info.get("upload_date", "")  # YYYYMMDD

	formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}" if upload_date else "unknown_date"

	return final_audio_path, video_title, uploader, formatted_date