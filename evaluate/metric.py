# import os
# import json
# import numpy as np
# from datasets import Dataset
# from dotenv import load_dotenv
# from ragas import evaluate
# from ragas.metrics import (
#     Faithfulness,
#     ContextRelevance,
#     # AnswerRelevancy
# )

# # ✅ Load API key từ .env
# load_dotenv()
# os.getenv("OPENAI_API_KEY")

# # ✅ Hàm load và chuẩn hóa dữ liệu từ file JSON
# def load_data_for_ragas(filepath):
#     with open(filepath, 'r', encoding='utf-8') as f:
#         raw_data = json.load(f)

#     data = []
#     for item in raw_data["review"]:
#         data.append({
#             "question": item["question"],
#             "answer": item["answer"],
#             "retrieved_contexts": item["context"],
#         })
#     return data

# # ✅ Hàm đánh giá RAGAS cho 1 file
# def evaluate_ragas(filepath, label):
#     data = load_data_for_ragas(filepath)
#     dataset = Dataset.from_list(data)
	
#     result = evaluate(
#         dataset,
#         metrics=[
#             Faithfulness(),
#             ContextRelevance(),
#             # AnswerRelevancy()
#         ]
#     )

#     return {
#         "model": label,
#         "faithfulness": np.mean(result["faithfulness"]),
#         "context_relevance": np.mean(result["nv_context_relevance"]),
#         # "answer_relevancy": np.mean(result["answer_relevancy"]),
#     }

# # ✅ Chạy đánh giá cho 1 file cụ thể
# filepath = "data/gemini_review.json"        # 🔁 thay đổi ở đây nếu muốn đánh giá file khác
# label = "gemini-1.5-flash"               # 🔁 tên model tương ứng

# print(f"🔍 Evaluating {label}...")
# result = evaluate_ragas(filepath, label)

# # ✅ In bảng kết quả
# print("\n📊 KẾT QUẢ ĐÁNH GIÁ RAGAS:")
# header = f"{'Model':<20} | {'Faithfulness':>12} | {'ContextRel':>12}"
# divider = "-" * len(header)
# print(header)
# print(divider)
# print(f"{result['model']:<20} | {result['faithfulness']:.4f}     | {result['context_relevance']:.4f}")



"""
Rouge score
"""
import json
from rouge_score import rouge_scorer
import numpy as np

def load_data_from_file(filepath):
	"""
	Loads review data from a JSON file
	Inputs:
		filepath (str): Path to the JSON file
	Output:
		list: A list of review entries
	"""

	with open(filepath, 'r', encoding='utf-8') as f:
		json_data = json.load(f)

	return json_data['review']

def context_to_reference(context_list):
	"""
	Converts a list of context strings into a single reference string
	Inputs:
		context_list (list): A list of context strings
	Output:
		str: A single string used as reference text
	"""

	return "\n".join(context_list)

def compute_rouge_against_context(answer, context_list):
	"""
	Computes ROUGE scores between an answer and its reference context
	Inputs:
		answer (str): The generated answer to evaluate
		context_list (list): A list of reference context strings
	Output:
		dict: A dictionary with ROUGE-1, ROUGE-2, and ROUGE-L scores
	"""

	reference = context_to_reference(context_list)
	scores = scorer.score(reference, answer)

	return {
		"rouge1": scores["rouge1"].fmeasure,
		"rouge2": scores["rouge2"].fmeasure,
		"rougeL": scores["rougeL"].fmeasure,
	}

def evaluate_file(filepath, label=None):
	"""
	Evaluates a review file by computing average ROUGE scores
	Inputs:
		filepath (str): Path to the review JSON file
		label (str, optional): Label to identify the model or file
	Output:
		dict: A dictionary containing the label and average ROUGE scores
	"""

	data = load_data_from_file(filepath)

	rouge1_list, rouge2_list, rougeL_list = [], [], []

	for sample in data:
		answer = sample["answer"]
		context = sample["context"]

		scores = compute_rouge_against_context(answer, context)

		rouge1_list.append(scores["rouge1"])
		rouge2_list.append(scores["rouge2"])
		rougeL_list.append(scores["rougeL"])

	return {
		"label": label or filepath,
		"rouge1": np.mean(rouge1_list),
		"rouge2": np.mean(rouge2_list),
		"rougeL": np.mean(rougeL_list),
	}

def print_comparison_table(results):
	"""
    Prints a formatted table comparing ROUGE scores across models
    Inputs:
        results (list): A list of dictionaries containing model labels and ROUGE scores
    Output:
        (prints to console)
    """

	print("====== ROUGE SCORES COMPARISON ======")

	header = f"{'Model':<20} | {'ROUGE-1':>9} | {'ROUGE-2':>9} | {'ROUGE-L':>9}"
	divider = "-" * len(header)

	print(header)
	print(divider)

	for result in results:
		model = result["label"]
		print(f"{model:<20} | {result['rouge1']:>9.4f} | {result['rouge2']:>9.4f} | {result['rougeL']:>9.4f}")

if __name__ == "__main__":
	scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

	# List of files and corresponding model names
	file_configs = [
		("data/gemini15_review.json", "gemini-1.5-flash"),
		("data/gemini25_review.json", "gemini-2.5-flash"),
		("data/deepseek_review.json", "deepseek-reasoner"),
		("data/gpt_review.json", "gpt-4-turbo"),
	]

	results = []

	for filepath, label in file_configs:
		result = evaluate_file(filepath, label)
		results.append(result)

	print_comparison_table(results)