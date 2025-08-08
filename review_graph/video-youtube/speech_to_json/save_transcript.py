import os
import json

def save_transcript(result, video_id, output_dir="video-youtube/review_data"):
    """
    Lưu kết quả transcript vào file JSON.

    Parameters:
    - result: dict chứa kết quả từ Whisper (đã chỉnh sửa nếu có).
    - video_id: ID của video.
    - output_dir: thư mục để lưu transcript.
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
