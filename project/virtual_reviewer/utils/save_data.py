import os
import json
from django.conf import settings

def save_data(question, answer, context, output_subdir="../evaluate/data"):
	"""
	Saves a review entry (question, answer, context) to a JSON file in the specified output directory
	Inputs:
		question (str): The review question
		answer (str): The generated answer
		context (list): A list of context strings used to generate the answer (specifications, reviewer data)
		output_subdir (str): Relative path to the output directory (default: "../evaluate/data")
	Output:
		str: The full file path of the updated JSON file
	"""

	output_dir = os.path.join(settings.BASE_DIR, output_subdir)
	os.makedirs(output_dir, exist_ok=True)

	# Used to save the review into the specified file
	# filepath = os.path.join(output_dir, "deepseek_review.json")
	# filepath = os.path.join(output_dir, "gpt_review.json")
	filepath = os.path.join(output_dir, "gemini_review.json")

	# If file exists, check contents
	if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
		with open(filepath, "r", encoding="utf-8") as f:
			try:
				existing_data = json.load(f)
			except json.JSONDecodeError:
				existing_data = {"review": []}
	else:
		existing_data = {"review": []}

	# Add new entry
	new_entry = {
		"question": question,
		"answer": answer,
		"context": context
	}
	existing_data["review"].append(new_entry)

	# Write back to file
	with open(filepath, "w", encoding="utf-8") as f:
		json.dump(existing_data, f, ensure_ascii=False, indent=2)

	print(f"✅ Đã cập nhật file data: {filepath}")

	return filepath