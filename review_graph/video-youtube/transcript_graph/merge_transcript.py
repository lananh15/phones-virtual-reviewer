import os
import json

TRANSCRIPT_DIR = "video-youtube/review_data"
output_file = "video-youtube/youtube_reviews.json"

merged_data = {"products": {}}

for filename in os.listdir(TRANSCRIPT_DIR):
    if filename.endswith(".json"):
        path = os.path.join(TRANSCRIPT_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            video_data = json.load(f)

        video_info = {
            "video_id": video_data.get("video_id"),
            "video_url": video_data.get("video_url"),
            "video_title": video_data.get("video_title"),
            "video_author": video_data.get("video_author"),
            "upload_date": video_data.get("upload_date")
        }

        for product in video_data.get("content", {}).get("products", []):
            name = product.get("name", "unknown_product")
            # Merge video info + product info
            product_entry = {
                **video_info,
                "features": product.get("features", []),
                "pros": product.get("pros", []),
                "cons": product.get("cons", []),
                "price": product.get("price", ""),
                "recommendation": product.get("recommendation", ""),
                "type": product.get("type", "")
            }

            if name not in merged_data["products"]:
                merged_data["products"][name] = []
            merged_data["products"][name].append(product_entry)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)

print("\n🧾 Danh sách sản phẩm đã merge:")
for idx, product_name in enumerate(merged_data["products"], start=1):
    print(f"{idx:>2}. {product_name}")

print(f"✅ Gộp xong, lưu vào {output_file}")
