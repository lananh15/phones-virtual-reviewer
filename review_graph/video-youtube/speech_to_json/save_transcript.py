import os
import json

def save_transcript(result, video_id, output_dir="video-youtube/review_data"):
	"""
	Saves a cleaned transcript of a YouTube video to a JSON file:
		- Extracts relevant metadata and content from the result dictionary
		- Creates the output directory if it doesn't exist
		- Writes the cleaned data to a JSON file named after the video ID
	Inputs:
		result (dict): Dictionary containing video metadata and transcript content
		video_id (str): Unique identifier for the video, used as the filename
		output_dir (str): Directory path where the JSON file will be saved (default: "video-youtube/review_data")
	Output:
		Creates a JSON file in the specified directory.
		Prints a success or error message to the console.
	"""

	os.makedirs(output_dir, exist_ok=True)

	cleaned = {
	  "video_id": result.get("video_id"),
	  "video_url": result.get("video_url"),
	  "video_title": result.get("video_title"),
	  "video_author": result.get("video_author"),
	  "upload_date": result.get("upload_date"),
	  "content": result.get("content"),
	}

	output_path = os.path.join(output_dir, f"{video_id}.json")

	try:
		with open(output_path, "w", encoding="utf-8") as f:
			json.dump(cleaned, f, ensure_ascii=False, indent=2)

		print(f"Saved transcript: {output_path}")

	except Exception as e:
		print(f"Error when saving transcript: {e}")