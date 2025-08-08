import os
from dotenv import load_dotenv
from handler.gpt_handler import GPTHandler
from tiktoken import encoding_for_model

load_dotenv()
gpt_api_key = os.getenv("OPENAI_API_KEY")
gpt = GPTHandler(gpt_api_key)

def count_tokens(text, model="gpt-4-turbo"):
    enc = encoding_for_model(model)
    return len(enc.encode(text))

def transcript_to_json(raw_text):
    """
    Gửi đoạn văn transcript thô tới GPT để chỉnh lỗi sai từ vựng theo ngữ cảnh.
    """
    prompt = f"""
    Bạn là một trợ lý AI hiểu tiếng Việt, chuyên xử lý transcript video review sản phẩm công nghệ là điện thoại.
    Dưới đây là đoạn transcript được chuyển từ giọng nói sang văn bản. Dù ngữ pháp có thể đúng, nhưng nội dung vẫn có thể chứa từ sai nghĩa hoặc lẫn ngữ cảnh, nên hãy đọc kỹ để phát hiện các từ nghe sai.

    Nhiệm vụ của bạn: Tổng hợp thông tin sản phẩm được đề cập trong video. Bao gồm cả:
    1. Sản phẩm chính được đánh giá trong video (nếu có),
    2. Các sản phẩm khác được mang ra so sánh, ví dụ như sản phẩm cũ hơn (iPhone 13, 14...) hoặc sản phẩm cùng tầm giá (Android...).
    Lưu ý:
    - Không tự thay đổi tên sản phẩm, trừ khi chắc chắn đó là lỗi nghe nhầm.
    - Giữ nguyên tên gốc nếu không có lý do rõ ràng để thay đổi.

    Với mỗi sản phẩm điện thoại, trích xuất thông tin dưới dạng JSON theo cấu trúc sau:
    - Tên sản phẩm (name)
    - Tính năng, đặc điểm được nhắc tới (features)
    - Ưu điểm được nhắc tới (pros)
    - Nhược điểm hoặc hạn chế (cons)
    - Mức giá nếu được đề cập (price)
    - Lý do nên mua, hoặc phù hợp với đối tượng nào (recommendation)
    - Loại đề cập: "main" nếu là sản phẩm điện thoại được review chính, "compare" nếu điện thoại chỉ được nhắc để so sánh (type)

    ⚠️ QUAN TRỌNG:
    - Chỉ trả về JSON hợp lệ, không thêm chú thích, markdown hoặc ký hiệu không hợp lệ.
    - Không bỏ sót bất kỳ thông tin nào về tính năng đặc điểm (bao gồm cả vẻ ngoài của điện thoại), ưu/nhược điểm, giá, hoặc nhận định từ người review (ví dụ như camera chụp ra màu sắc cụ thể thế nào).
    - Tuyệt đối **không được lược bỏ hoặc rút gọn** thành kiểu `"pin tốt"` hoặc `"thời lượng pin ổn"` nếu trong transcript có chi tiết cụ thể hơn và phải liệt kê càng rõ và chi tiết càng tốt.
    - Ví dụ:
        ❌ Không đúng: `"camera chất lượng cao"`
        ✅ Đúng: `"camera chính 50MP"`, `"quay video 4K 60fps"`, `"chế độ chụp đêm tốt"`
    - Nếu không có thông tin thì để trống `[]` hoặc `""` đúng định dạng yêu cầu – tuyệt đối không được tự chế thêm thông tin.
    - Mọi dữ liệu phải ghi bằng tiếng Việt (trừ các tên sản phẩm hoặc thuật ngữ công nghệ tiếng Anh).

    ▶️ Format JSON bắt buộc phải đầy đủ như dưới đây:
    {{
    "products": [
        {{
        "name": "tên sản phẩm",
        "features": ["tính năng 1", "tính năng 2"] (nếu không được đề cập trong transcript thì ghi rỗng []),
        "pros": ["điểm mạnh 1", "điểm mạnh 2"] (nếu không được đề cập trong transcript thì ghi rỗng []),
        "cons": ["điểm yếu 1", "điểm yếu 2"] (nếu không được đề cập trong transcript thì ghi rỗng []),
        "price": "giá tiền (nếu không được đề cập trong transcript thì ghi rỗng "")",
        "recommendation": "lý do nên mua (nếu không được đề cập trong transcript thì ghi rỗng "")",
        "type": "main" hoặc "compare"
        }}
    ]
    }}

    Transcript gốc:
    {raw_text}
    """
    try:
        print("Token: ", count_tokens(prompt))

        response = gpt.invoke([
            {"role": "system", "content": "Bạn là một trợ lý AI giỏi tiếng Việt, hiểu transcript và tổng hợp thông tin review sản phẩm công nghệ."},
            {"role": "user", "content": prompt}
        ])

        if response.startswith("```json"):
            response = response.replace("```json", "").replace("```", "").strip()
        elif response.startswith("```"):
            response = response.replace("```", "").strip()

        return response
    except Exception as e:
        print(f"❌ Lỗi gọi GPT API: {e}")
        return raw_text