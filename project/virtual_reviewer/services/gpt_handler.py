import json
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from ..utils.review_utils import *

load_dotenv()

class GPTHandler:
	def __init__(self):
		api_key = os.getenv('OPENAI_API_KEY')
		self.llm = ChatOpenAI(openai_api_key=api_key, model_name="gpt-4-turbo", temperature=0)

	def invoke(self, messages, max_tokens=6000):
		"""
		Sends a list of messages to the GPT model and returns the response
		Inputs:
			messages (list): A list of message dictionaries with 'role' and 'content'
			max_tokens (int): Maximum number of tokens to generate (default: 6000)
		Output:
			str: The trimmed response content from GPT
		"""

		return self.llm.invoke(messages, config={"max_tokens": max_tokens}).content.strip()
	
	def generate_review(self, prompt):
		"""
		Generates a structured review from a prompt using the GPT model
		Inputs:
			prompt (str): The user prompt containing review context
		Output:
			tuple: (raw response string, formatted review answer)
		Raises:
			ValueError: If the response is not valid JSON
		"""

		print("Using gpt-4-turbo")

		response = self.invoke([
			{"role": "system", "content": "Bạn là AI chuyên tổng hợp review, chỉ trả về JSON **duy nhất**, không bao gồm bất kỳ lời chào hay văn bản ngoài JSON và đóng mở ngoặc vuông, ngoặc nhọn đúng JSON object (Chỉ trả về JSON được parse thành công bởi json.loads()). NHIỆM VỤ TUYỆT ĐỐI: 1) PHẢI sử dụng ĐẦY ĐỦ TẤT CẢ thông tin của mỗi reviewer - KHÔNG ĐƯỢC BỎ SÓT BẤT KỲ ITEM NÀO. 2) Đặc biệt chú ý những cons ít phổ biến như 'pin suy giảm', 'không hỗ trợ AI', 'không có Action Button' - những cái này dễ bị bỏ sót nhất. 3) Trước khi trả về JSON, phải đối chiếu lại với data gốc từng reviewer một để đảm bảo không thiếu thông tin nào kể cả tên sản phẩm khác."},
			{"role": "user", "content": prompt}
		])

		# print(f"""Prompt: {prompt}""")
		cleaned = clean_json_response(response)
		# print(f"""Response: {cleaned}""")

		try:
			response_json = json.loads(cleaned)
		except json.JSONDecodeError as e:
			print("❌ Lỗi khi parse JSON từ GPT:", e)
			raise ValueError("GPT trả về không phải JSON hợp lệ")

		answer = get_answer(response_json["data"][0])

		return response, answer