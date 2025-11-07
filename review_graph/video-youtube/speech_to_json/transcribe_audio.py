# import whisper
# import torch

# MODEL_SIZE = "small"
# LANG = "vi"

# def transcribe(audio_path):
#     """
#     Chạy Whisper một lần duy nhất để transcribe.
#     """
#     model = whisper.load_model(MODEL_SIZE).to("cuda" if torch.cuda.is_available() else "cpu")

#     context = (
#         "Video review bằng tiếng Việt về điện thoại smartphone (có thể kèm 1 số từ tiếng Anh chuyên dùng trong công nghệ điện thoại)"
#         "Từ khóa: iPhone Samsung Xiaomi Realme camera pin màn hình Snapdragon RAM hiệu năng Hz điểm mạnh điểm yếu mua."
#     )

#     result = model.transcribe(
#         audio_path,
#         language=LANG,
#         initial_prompt=context,
#         temperature=0.0,
#         best_of=3,
#         condition_on_previous_text=False
#     )
#     print(f"Text from Whisper: {result['text']}")
#     return result

import faster_whisper
import torch

MODEL_SIZE = "small"
LANG = "vi"

def transcribe(audio_path):
	"""
	Transcribes Vietnamese audio using the Faster-Whisper model:
		- Loads the Whisper model with GPU support if available
		- Uses an initial prompt to guide transcription for phone review content
		- Transcribes the audio file and returns the full text and detected language
	Inputs:
		audio_path (str): Path to the audio file to be transcribed
	Output:
		dict: A dictionary containing:
			- "text" (str): The full transcribed text
			- "language" (str): The detected language of the audio
	"""

	device = "cuda" if torch.cuda.is_available() else "cpu" # cuda if use GPU
	model = faster_whisper.WhisperModel(MODEL_SIZE, device=device, compute_type="int8")

	initial_prompt = (
		"Đây là video đánh giá điện thoại bằng tiếng Việt. "
		"Từ khóa: iPhone, Samsung, Oppo, Xiaomi, Realme, Vivo, camera, màn hình, hiệu năng, pin, sạc nhanh, Snapdragon, RAM, Hz, giá bán, điểm mạnh, điểm yếu đánh giá, so sánh."
	)

	segments, info = model.transcribe(
		audio_path,
		language=LANG,
		beam_size=5,
		vad_filter=False,
		initial_prompt=initial_prompt
	)

	full_text = " ".join([seg.text.strip() for seg in segments])
	# print(f"Text from Faster-Whisper: {full_text}")

	# with open("output.txt", "w", encoding="utf-8") as f:
	#	f.write(full_text)

	return {
		"text": full_text,
		"language": info.language
	}