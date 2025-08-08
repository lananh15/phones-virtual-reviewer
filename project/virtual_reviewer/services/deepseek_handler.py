import os
import json
import requests
from dotenv import load_dotenv
from ..utils.review_utils import *

load_dotenv()

class ChatDeepSeek:
    def __init__(self, model, deepseek_api_key, temperature=0.0):
        self.model = model
        self.api_key = deepseek_api_key
        self.temperature = temperature
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    def invoke(self, messages):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"❌ DeepSeek API lỗi: {response.status_code} - {response.text}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]

class DeepSeekHandler:
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("❌ DEEPSEEK_API_KEY chưa được đặt trong .env")
        
        self.llm = ChatDeepSeek(
            model="deepseek-reasoner",
            deepseek_api_key=api_key,
            temperature=0
        )

    def invoke(self, messages):
        return self.llm.invoke(messages).strip()

    def generate_review(self, prompt):
        print("Using deepseek-reasoner")  
        response = self.invoke([
            {
                "role": "system",
                "content": "Bạn là AI chuyên tổng hợp review. NHIỆM VỤ TUYỆT ĐỐI: 1) PHẢI sử dụng ĐẦY ĐỦ TẤT CẢ thông tin của mỗi reviewer - KHÔNG ĐƯỢC BỎ SÓT BẤT KỲ ITEM NÀO. 2) Đặc biệt chú ý những cons ít phổ biến như 'pin suy giảm', 'không hỗ trợ AI', 'không có Action Button' - những cái này dễ bị bỏ sót nhất. 3) Trước khi trả về JSON, phải đối chiếu lại với data gốc từng reviewer một để đảm bảo không thiếu thông tin nào kể cả tên sản phẩm khác."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])
        # print(f"📤 Prompt gửi lên:\n{prompt}\n")
        cleaned = clean_json_response(response)
        # print(f"📥 Response đã clean:\n{cleaned}\n")
        try:
            response_json = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print("❌ Lỗi khi parse JSON từ DeepSeek:", e)
            raise ValueError("DeepSeek trả về không phải JSON hợp lệ")

        answer = get_answer(response_json["data"][0])
        return cleaned, answer
