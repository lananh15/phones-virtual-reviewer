import json
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from ..utils.review_utils import *

load_dotenv()

class GeminiHandler:
	def __init__(self):
		api_key = os.getenv("GOOGLE_API_KEY")
		self.llm = ChatGoogleGenerativeAI(
			model="gemini-2.5-flash",
			google_api_key=api_key,
			temperature=0
		)

	def invoke(self, messages):
		"""
		Sends a list of messages to the Gemini model and returns the response
		Inputs:
			messages (list): A list of message dictionaries with 'role' and 'content'
		Output:
			str: The trimmed response content from Gemini
		"""

		return self.llm.invoke(messages).content.strip()
	
	def generate_review(self, prompt):
		"""
		Generates a structured review from a prompt using the Gemini model
		Inputs:
			prompt (str): The user prompt containing review context
		Output:
			tuple: (cleaned JSON string, formatted review answer)
		Raises:
			ValueError: If the response is not valid JSON
		"""
  
		print("Using gemini-2.5-flash") 

		response = self.invoke([
			{"role": "system", "content": "Bạn là AI chuyên tổng hợp review. NHIỆM VỤ TUYỆT ĐỐI: 1) PHẢI sử dụng ĐẦY ĐỦ TẤT CẢ thông tin của mỗi reviewer - KHÔNG ĐƯỢC BỎ SÓT BẤT KỲ ITEM NÀO. 2) Đặc biệt chú ý những cons ít phổ biến như 'pin suy giảm', 'không hỗ trợ AI', 'không có Action Button' - những cái này dễ bị bỏ sót nhất. 3) Trước khi trả về JSON, phải đối chiếu lại với data gốc từng reviewer một để đảm bảo không thiếu thông tin nào kể cả tên sản phẩm khác."},
			{"role": "user", "content": prompt}
		])

		# print(f"""Prompt: {prompt}""")
		cleaned = clean_json_response(response)
		# print(f"""Response: {cleaned}""")

		try:
			response_json = json.loads(cleaned)
		except json.JSONDecodeError as e:
			print("❌ Lỗi khi parse JSON từ Gemini:", e)
			raise ValueError("Gemini trả về không phải JSON hợp lệ")

		answer = get_answer(response_json["data"][0])

		return cleaned, answer