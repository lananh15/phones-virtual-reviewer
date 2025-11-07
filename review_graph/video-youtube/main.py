import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)).replace("video-youtube", ""))

from speech_to_json.download_audio import download_audio, extract_video_id
from speech_to_json.transcribe_audio import transcribe
from speech_to_json.transcript_processor import transcript_to_json
from speech_to_json.save_transcript import save_transcript
import json
from yt_dlp import YoutubeDL
from utils.ffmpeg_download import download_ffmpeg_if_needed

ffmpeg_dir = download_ffmpeg_if_needed()
os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

AUDIO_DIR = "video-youtube/audio"
TRANSCRIPT_DIR = "video-youtube/review_data"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def process_batch(link_file):
	"""
	Processes a batch of YouTube video links to extract and save structured review data:
		- Reads a list of YouTube URLs from a text file
		- Extracts the video ID from each URL
		- Downloads the audio if not already present
		- Retrieves video metadata (title, author, upload date)
		- Transcribes the audio using Whisper
		- Sends the transcript to an LLM to extract structured review data in JSON format
		- Saves the final transcript and metadata to a JSON file
	Inputs:
		link_file (str): Path to a text file containing YouTube video URLs (one per line)
	Output:
		None
	Side Effects:
		- Creates audio and transcript directories if they don't exist
		- Downloads audio files and saves them locally
		- Writes transcript JSON files to disk
		- Prints progress and error messages to the console
	"""

	with open(link_file, "r") as f:
		urls = [line.strip() for line in f if line.strip()]

	for url in urls:
		video_id = extract_video_id(url)

		if not video_id:
			print(f"Skip invalid link: {url}")
			continue

		print(f"\n▶️ Processing: {video_id}")

		audio_path = os.path.join(AUDIO_DIR, f"{video_id}.mp3")
		transcript_path = os.path.join(TRANSCRIPT_DIR, f"{video_id}.json")

		if os.path.exists(transcript_path):
			print(f"Have review_data: {video_id}, skip.")
			continue

		if not os.path.exists(audio_path):
			try:
				print("Downloading audio...")
				downloaded_audio_path, video_title, video_author, upload_date = download_audio(url, video_id, AUDIO_DIR, ffmpeg_dir)
			except Exception as e:
				print(f"Error when downloading {video_id}: {e}")
				continue
		else:
			downloaded_audio_path = audio_path
			try:
				with YoutubeDL({'quiet': True}) as ydl:
					info = ydl.extract_info(url, download=False)
					video_title = info.get("title", "unknown_title")
					video_author = info.get("uploader", "unknown_author")
					upload_date = info.get("upload_date", "unknown_date")
			except:
				video_title = "unknown_title"
				video_author = "unknown_author"
				upload_date = "unknown_date"

		try:
			if not os.path.exists(downloaded_audio_path):
				print("❌ Audio doesn't exist after downloading.")
				continue

			print("Run Whisper...")
			result = transcribe(downloaded_audio_path)

			corrected_text_str = transcript_to_json(result["text"])

			try:
				summary_json = json.loads(corrected_text_str)
			except json.JSONDecodeError as e:
				print(f"❌ JSON error: {e}")
				summary_json = {"error": "cannot parse"}

			result.update({
			  "video_id": video_id,
			  "video_url": url,
			  "video_title": video_title,
			  "video_author": video_author,
			  "upload_date": upload_date,
			  "content": summary_json
			})

			save_transcript(result, video_id)

			print(f"Done: {video_id} - {video_title}")

		except Exception as e:
			print(f"Error with {video_id}: {e}")
			import traceback
			print(f"Error: {traceback.format_exc()}")

if __name__ == "__main__":
	process_batch("video-youtube/youtube_links.txt")