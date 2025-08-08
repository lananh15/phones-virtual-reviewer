import os
import json
from django.conf import settings

def save_data(question, answer, context, output_subdir="../evaluate/data"):
    output_dir = os.path.join(settings.BASE_DIR, output_subdir)
    os.makedirs(output_dir, exist_ok=True)

    # Dùng để ghi review vào file đo
    # filepath = os.path.join(output_dir, "deepseek_review.json")
    # filepath = os.path.join(output_dir, "gpt_review.json")
    filepath = os.path.join(output_dir, "gemini_review.json")

    # Nếu file đã tồn tại, kiểm tra nội dung
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {"review": []}
    else:
        existing_data = {"review": []}

    # Thêm dữ liệu mới
    new_entry = {
        "question": question,
        "answer": answer,
        "context": context
    }
    existing_data["review"].append(new_entry)

    # Ghi lại file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã cập nhật file data: {filepath}")
    return filepath
