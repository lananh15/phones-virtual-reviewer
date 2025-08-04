import json
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class GPTHandler:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        self.llm = ChatOpenAI(openai_api_key=api_key, model_name="gpt-4-turbo", temperature=0)

    def invoke(self, messages, max_tokens=6000):
        return self.llm.invoke(messages, config={"max_tokens": max_tokens}).content.strip()
    
    def generate_review(self, product_name, reviewers):
        reviewer_count = len(reviewers)
        reviewer_names = [r.get('author', 'Unknown') for r in reviewers]
        
        prompt = f"""
        NHIỆM VỤ: Viết bài review tổng hợp (bằng tiếng Việt với giọng điệu tự nhiên, chuyên nghiệp như các reviewer điện thoại) cho sản phẩm "{product_name}" từ {reviewer_count} reviewer.

        DANH SÁCH {reviewer_count} REVIEWER CẦN XỬ LÝ:
        {', '.join([f"{i+1}. {name}" for i, name in enumerate(reviewer_names)])}

        DỮ LIỆU REVIEWER:
        {json.dumps(reviewers, ensure_ascii=False, indent=2)}

        QUY TRÌNH BẮT BUỘC:

        BƯỚC 1: KIỂM TRA ĐẦU VÀO
        - Xác nhận đã đọc thông tin của tất cả {reviewer_count} reviewer
        - Ghi nhận reviewer nào có type="main" (tức là {product_name} được review chính trong video) và type="compare" (tức là {product_name} được so sánh với sản phẩm chính nào đó trong video)
        - Liệt kê reviewer nào có pros/cons đầy đủ, reviewer nào chỉ có recommendation/price

        BƯỚC 2: PHÂN LOẠI VÀ GOM NHÓM THÔNG TIN (QUAN TRỌNG)
        - **LIỆT KÊ ĐẦY ĐỦ TRƯỚC KHI GOM NHÓM**: Đọc kỹ và ghi rõ TẤT CẢ pros/cons từ mỗi reviewer (kể cả những điểm ít phổ biến như "pin suy giảm", "không AI", etc.), đọc kèm feature kĩ lưỡng vì có 1 số tính năng có đề cập liên quan đến pros/cons
        - **Xác định ý tương đồng**: Trước khi viết, liệt kê các ý kiến có cùng nghĩa:
        * VD: "nặng", "khó cầm một tay", "kích thước lớn khó thao tác" → GOM THÀNH 1 NHÓM
        * VD: "cổng Lightning", "không có Type-C" → GOM THÀNH 1 NHÓM  
        * VD: "thiết kế sang trọng", "ngoại hình đẹp", "viền thép bóng" → GOM THÀNH 1 NHÓM
        - Pros: Gom tất cả ưu điểm (nhóm các ý kiến giống nhau lại nếu có, và vẫn giữ những ý kiến riêng)
        - Cons: Gom tất cả nhược điểm (nhóm các ý kiến giống nhau lại nếu có, và vẫn giữ những ý kiến riêng)
        - Features: Gom tất cả tính năng được đề cập
        - Price: Gom thông tin giá từ các reviewer  
        - Recommendations: Gom tất cả lời khuyên
        - **BẮT BUỘC**: Không được bỏ sót bất kì thông tin nào, đặc biệt các cons/pros ít phổ biến

        BƯỚC 3: VIẾT BÀI REVIEW
        Format JSON chuẩn với các yêu cầu:

        1. INTRO thu hút, hấp dẫn (150-200 từ): 
        - Giới thiệu về {product_name} thu hút độc giả
        - Lý do vì sao sản phẩm này vẫn được quan tâm
        - Đề cập "tổng hợp từ {reviewer_count} reviewer gồm: [liệt kê tên]"
        - Nêu mục đích bài review và đối tượng độc giả

        2. PROS: Mỗi ưu điểm phải có format:
        Nếu thông tin đó chỉ có 1 reviewer đề cập thì vẫn phải ghi (không được bỏ sót) "Theo [Author], [ưu điểm cụ thể] (video đăng ngày [upload_date], [url])"
        Nếu có nhiều reviewer cùng chung ý kiến thì gom chung "Theo A, B, C, [ưu điểm cụ thể] (trích dẫn các video đăng ngày [upload_date], [url]))"
        **QUAN TRỌNG - TRÁNH LẶP TỪ "THEO"**: 
        - Đa dạng cách trích dẫn: "[Author] nhận định...", "[Author] cho biết...", "Reviewer [Author] đánh giá...", "Trong quan điểm của [Author]...", "[Author] ghi nhận..."
        - Nếu nhiều reviewer cùng ý: "Cả [A] và [B] đều nhấn mạnh...", "Nhiều reviewer như [A], [B] đồng thuận..."
        - Tích hợp tự nhiên vào câu, không cứng nhắc

        3. CONS: Tương tự pros với format trích dẫn đầy đủ

        4. SUGGESTION: 
        - Tổng hợp từ TẤT CẢ {reviewer_count} reviewer
        - Nếu reviewer nào không có data thì bỏ qua

        KIỂM TRA CUỐI:
        - Đã sử dụng thông tin từ tất cả {reviewer_count} reviewer
        - **KHÔNG LẶP TỪ "THEO"** quá nhiều lần trong toàn bài
        - Mỗi pros/cons có trích dẫn đầy đủ (author, ngày, link)  
        - Không bỏ sót reviewer nào có type="compare"
        - Suggestion tổng hợp từ nhiều góc nhìn
        - **ĐẶC BIỆT**: Kiểm tra lại có bỏ sót cons/pros nào không (VD: "pin suy giảm", "không AI", etc.)

        YÊU CẦU ĐẶC BIỆT:
        - KHÔNG được bỏ sót bất kỳ reviewer nào trong danh sách
        - **BẮT BUỘC GOM NHÓM**: Các ý kiến có cùng nghĩa phải được gom lại (VD: "nặng", "khó cầm", "kích thước lớn" → 1 điểm về ergonomics)
        - **KHÔNG LẶP Ý**: Mỗi vấn đề chỉ xuất hiện 1 lần, dù có nhiều reviewer đề cập
        - **KHÔNG LẶP TỪ**: Tuyệt đối tránh lặp "Theo [Author]"" quá nhiều lần
        - **KHÔNG BỎ SÓT**: Dù reviewer có ít data (chỉ recommendation hoặc price) vẫn phải đưa vào, không được bỏ sót
        - **COVERAGE ĐẦY ĐỦ**: Mỗi item trong pros/cons array của reviewer phải xuất hiện trong response
        - Nếu reviewer có pros/cons rỗng nhưng có recommendation → đưa vào suggestion
        - Độ dài: 1200-1500 từ
        - Format JSON chuẩn

        {{
        "data": [{{
            "title": "[Tiêu đề sáng tạo, nổi bật và thu hút người xem về {product_name} (không đặt tên trùng với tên các video review, hoặc quá đơn giản như "Đánh Giá Tổng Hợp Từ Các Chuyên Gia Công Nghệ")]",
            "intro": "[150-200 từ: Giới thiệu chi tiết + tổng hợp từ {reviewer_count} reviewer]",
            "features": "[250-300 từ: Mô tả chi tiết tính năng với trích dẫn nguồn]",
            "pros": [
            "[Mỗi điểm viết 3-4 câu giải thích chi tiết với trích dẫn đầy đủ]"
            ],
            "cons": [
            "[Mỗi điểm viết 3-4 câu giải thích tác động với trích dẫn đầy đủ]"
            ],
            "price_analysis": "[100-150 từ: Phân tích giá và định vị sản phẩm]",
            "suggestion": "[150-200 từ: Tổng hợp từ TẤT CẢ {reviewer_count} reviewer]"
        }}]
        }}

        **VALIDATION BẮT BUỘC TRƯỚC KHI TRẢ VỀ:**
        - Kiểm tra từng reviewer: có item nào trong pros/cons/features/recommendation array bị thiếu không?
        - Kiểm tra tất cả reviewer khác có cons/pros/features/recommendation nào bị bỏ sót không?
        - **Kiểm tra không lặp từ "Theo [Author]" quá nhiều lần trong toàn bài**

        LƯU Ý: Trước khi trả về JSON, hãy đảm bảo đã sử dụng thông tin từ TẤT CẢ {reviewer_count} reviewer trong danh sách và không bỏ sót bất kỳ pros/cons nào.
        """                
        response = self.invoke([
            {"role": "system", "content": "Bạn là AI chuyên tổng hợp review. NHIỆM VỤ TUYỆT ĐỐI: 1) PHẢI sử dụng ĐẦY ĐỦ TẤT CẢ thông tin trong pros/cons array của mỗi reviewer - KHÔNG ĐƯỢC BỎ SÓT BẤT KỲ ITEM NÀO. 2) Đặc biệt chú ý những cons ít phổ biến như 'pin suy giảm', 'không hỗ trợ AI', 'không có Action Button' - những cái này dễ bị bỏ sót nhất. 3) Trước khi trả về JSON, phải đối chiếu lại với data gốc từng reviewer một để đảm bảo không thiếu thông tin nào."},
            {"role": "user", "content": prompt}
        ])
                            
        return response