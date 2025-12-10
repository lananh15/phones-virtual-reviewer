from django.http import JsonResponse
from .user import UserViews
from ..utils.save_data import *
from ..utils.review_utils import *

class GenerateReviewView(UserViews):
	def get(self, request):
		"""
		Handle GET request to generate a summarized product review
		Input:
			Product name from query params
		Output:
			JSON containing LLM-generated review and video title mapping
		"""

		product_name = request.GET.get("name", "")
		# print(f"🔍 Tạo review cho sản phẩm: {product_name}")

		if not product_name:
			return JsonResponse({"error": "Thiếu tên sản phẩm"}, status=400)

		query = """
		MATCH (p:Product {name: $product_name})-[:MENTIONED_IN]->(r:VideoReview)-[:IN_VIDEO]->(v:Video)
		OPTIONAL MATCH (r)-[:HAS_PRO]->(pro:Pro)
		OPTIONAL MATCH (r)-[:HAS_CON]->(con:Con)
		OPTIONAL MATCH (r)-[:HAS_FEATURE]->(feat:Feature)
		RETURN
		v.video_id AS video_id,
		v.title AS title,
		v.url AS url,
		v.upload_date AS upload_date,
		v.author AS author,

		r.price AS price,
		r.recommendation AS recommendation,
		r.type AS type,

		collect(DISTINCT pro.text) AS pros,
		collect(DISTINCT con.text) AS cons,
		collect(DISTINCT feat.text) AS features
		ORDER BY v.upload_date DESC
		"""

		# Manufacturer info query
		nsx_query = """
		MATCH (p:Product {name: $product_name})
		OPTIONAL MATCH (p)-[:HAS_GENERAL_INFO]->(g:GeneralInfo)
		OPTIONAL MATCH (p)-[:HAS_HARDWARE]->(hw:HardwareSpec)
		OPTIONAL MATCH (p)-[:HAS_SOFTWARE]->(sw:SoftwareSpec)
		OPTIONAL MATCH (p)-[:HAS_CAMERA]->(cam:CameraSpec)
		OPTIONAL MATCH (p)-[:HAS_DISPLAY]->(disp:DisplaySpec)
		OPTIONAL MATCH (p)-[:HAS_DISPLAY_FEATURE]->(df:DisplayFeature)
		OPTIONAL MATCH (p)-[:HAS_HARDWARE]->(nfc:HardwareSpec)
		WHERE toLower(nfc.key) = "nfc"
		RETURN
		g.model AS model,
		g.link AS link,
		g.price AS nsx_price,
		collect(DISTINCT CASE WHEN toLower(hw.key) <> "nfc" THEN hw.key + ": " + hw.value ELSE NULL END) AS hardware_specs,
		CASE
			WHEN toLower(nfc.value) = "true" THEN "Có"
			WHEN toLower(nfc.value) = "false" THEN "Không"
			ELSE "Không rõ"
		END AS nfc_support,
		sw.os AS os,
		collect(DISTINCT 
			CASE 
				WHEN toLower(cam.type) = "rear" THEN "Camera sau: " + cam.detail
				WHEN toLower(cam.type) = "front" THEN "Camera trước: " + cam.detail
				ELSE cam.type + ": " + cam.detail
			END
		) AS camera_specs,
		disp.technology AS display_tech,
		disp.size AS display_size,
		disp.resolution AS display_resolution,
		collect(DISTINCT df.text) AS display_features
		"""

		try:
			with self.neo4j_handler as db:
				result = db.run_read_query(query, {"product_name": product_name})
				product_info_records = db.run_read_query(nsx_query, {"product_name": product_name})

				if not product_info_records:
					return JsonResponse({"error": "Không tìm thấy sản phẩm trong database"}, status=404)
				product_info = product_info_records[0]

		except Exception as e:
			return JsonResponse({
				"error": "Lỗi kết nối hoặc truy vấn dữ liệu, vui lòng thử lại sau.",
				"detail": "Neo4j error"
			}, status=503)
		
		# Convert to reviewer format
		reviewers = []
		video_title_map = {}
		for row in result:
			if row.get("url") and row.get("title"):
				video_title_map[row["url"]] = row["title"]

			reviewer = {
				"author": row.get("author"),
				"video_id": row.get("video_id"),
				"title": row.get("title"),
				"url": row.get("url"),
				"upload_date": row.get("upload_date"),
				"price": row.get("price"),
				"recommendation": row.get("recommendation"),
				"type": row.get("type"),
				"pros": [p for p in row.get("pros", []) if p],
				"cons": [c for c in row.get("cons", []) if c],
				"features": [f for f in row.get("features", []) if f],
			}
			reviewers.append(reviewer)

		question = f"""Hãy viết bài review tổng hợp (bằng tiếng Việt với giọng điệu tự nhiên, chuyên nghiệp như các reviewer điện thoại) cho sản phẩm "{product_name}" từ reviewers. Bài viết cần đầy đủ tính năng, ưu điểm, nhược điểm, giá và gợi ý sản phẩm này phù hợp với ai."""
		context = get_context(reviewers, product_info)
		prompt = f"""
		NHIỆM VỤ:
		Viết bài review tổng hợp (bằng tiếng Việt, giọng điệu tự nhiên, chuyên nghiệp như các reviewer công nghệ Việt Nam) cho sản phẩm "{product_name}" từ reviewers.

		DỮ LIỆU REVIEW ĐÃ ĐƯỢC TIỀN XỬ LÝ:
		⚠️ Mọi dữ liệu bên dưới — dù nằm trong video tiêu đề là sản phẩm khác — đều là **nhận xét trực tiếp về sản phẩm "{product_name}"**.
		→ Vì các video đó có nhắc đến "{product_name}" để so sánh, nên toàn bộ nội dung đều liên quan và **phải được xử lý đầy đủ**.
		→ Không được bỏ sót bất kỳ dòng nào chỉ vì tiêu đề video không trùng với tên sản phẩm.
		→ Không được bỏ bất kỳ tên sản phẩm nào khác được đề cập, giữ nguyên nội dung chứa tên sản phẩm khác đó vào bài review bạn viết để mang lại nhiều góc nhìn khách quan cho người đọc.

		{context}

		---
		🚨 BẮT BUỘC - LIỆT KÊ TẤT CẢ SO SÁNH TRƯỚC KHI VIẾT:
		Trước khi viết bài, hãy LIỆT KÊ TOÀN BỘ các câu có chứa so sánh trong dữ liệu (bao gồm **Tính năng**, **Ưu điểm**, **Nhược điểm**, **Giá**, **Khuyến nghị** từ các reviewer):
		- Tìm tất cả câu có chứa tên sản phẩm khác như "iPhone 13", "iPhone 14 Pro", "Oppo Find X8", "Samsung Galaxy S24", v.v.  
		- Ghi rõ reviewer nào nói gì và không được lược bỏ bất kì tên sản phẩm nào được đề cập
		- VÍ DỤ: "Camera tương đương iPhone 14 Pro" → TẤT CẢ những so sánh này PHẢI xuất hiện trong bài viết cuối cùng!

		🔍 NGUYÊN TẮC XỬ LÝ THÔNG TIN SO SÁNH:
		- Nếu câu có đề cập đến sản phẩm khác (ví dụ: iPhone 15 Pro Max), thì tức là đang **so sánh với {product_name}** hoặc **"{product_name} đang được so sánh với sản phẩm đó"**.
		- Tất cả các so sánh này đều là **nhận xét về {product_name}**, vì vậy **phải được ghi lại đầy đủ**.
		- Mỗi nhận xét có yếu tố so sánh cần được viết thành **đoạn riêng biệt**, không được gộp chung với những ý không có so sánh.
		- Ví dụ:
			- “Viền thép đẹp hơn iPhone 15 Pro Max” là **ưu điểm của {product_name}**, phải giữ nguyên tên sản phẩm được đề cập là iPhone 15 Pro Max
			- “Nặng hơn iPhone 13 Pro Max” là **nhược điểm của {product_name}**, phải giữ nguyên tên sản phẩm được đề cập là iPhone 13 Pro Max

		⚠️ QUAN TRỌNG - XỬ LÝ TÊN SẢN PHẨM KHÁC:
		- Nếu có đề cập sản phẩm nào khác như "iPhone 15 Pro Max", "iPhone 13 Pro Max", "Samsung Galaxy S25", v.v. → BẮT BUỘC phải giữ NGUYÊN TÊN trong bài viết
		- VÍ DỤ: "viền thép đẹp hơn so với viền Titan của iPhone 15 Pro Max" → PHẢI viết y nguyên như vậy  
		- KHÔNG được viết thành "viền thép đẹp hơn các đời sau" hay "viền thép đẹp hơn"
		- MỖI LẦN so sánh = MỖI LẦN phải ghi rõ tên sản phẩm được so sánh
		---

		✅ TRÌNH TỰ THỰC HIỆN:

		🔹 **BƯỚC 1 – CHECKLIST REVIEWER:**
		- Liệt kê toàn bộ reviewer, dù chỉ có 1 dòng dữ liệu.
		- Với mỗi reviewer, ghi:
			[Tên reviewer] + [số lượng pros/cons] + [có/không có recommendation] + (type = "main"/"compare")

		🔹 **BƯỚC 2 – PHÂN TÍCH RIÊNG TỪNG REVIEWER:**
		- Với mỗi reviewer: trích đầy đủ phần pros, cons, features, price, recommendation (nếu có).
		- Không được thiếu reviewer nào dù chỉ có 1 nhận xét.

		🔹 **BƯỚC 3 – GOM NHÓM VÀ VIẾT THÀNH BÀI:**
		- Mỗi nội dung pros/cons/feature/recommendation chỉ viết **một lần duy nhất** (trừ nội dung có yếu tố so sánh với sản phẩm khác).
		- Nếu nhiều reviewer nói cùng một ý nội dung:
			→ Gom lại thành một đoạn.
			→ Ghi rõ tất cả reviewer + trích dẫn theo format: [url - author đăng ngày upload_date]
		- Nếu có sự khác biệt trong nội dung:
			→ Viết thành các đoạn khác nhau.
		- Nếu một reviewer nói **cùng ý với các reviewer khác nhưng lại có yếu tố so sánh với sản phẩm khác**, thì:
			→ Viết trong cùng ĐOẠN nội dung, nhưng tách thành **nhiều câu**, mỗi câu ghi rõ nội dung PHẢI CHỨA cả tên sản phẩm khác được so sánh và trích dẫn.
		- Tuyệt đối không được bỏ sót bất kỳ ý nào chỉ vì “giống nhau phần nào”.
		- Các [Tên sản phẩm] khác được đề cập **bắt buộc phải giữ nguyên**.
		- Bất kì ưu nhược điểm nào cũng phải đề cập chi tiết nếu reviewer có mô tả chi tiết. Ví dụ: không được tóm gọn như "camera chất lượng tốt" trong khi review đề cập "camera quay đẹp, chụp hình thiếu sáng tốt, HDR..."

		---

		🎯 NGUYÊN TẮC BẮT BUỘC:
		- Không được viết lặp lại cùng một ý quá 1 lần (trừ nội dung có yếu tố so sánh với sản phẩm khác).
		- Có thể dùng nhiều reviewer cho cùng một đoạn.
		- Không lặp lại cụm “Theo [Author]” quá 3 lần — thay bằng: “chia sẻ”, “cho biết”, “trong nhận định của”, v.v.
		- Không được tự diễn giải hoặc thêm nội dung không có trong dữ liệu.
		- Không được lược bỏ tên sản phẩm khác nếu có đề cập.
		- MỖI Ý KIẾN PHẢI CÓ TRÍCH DẪN theo format: **[url - author đăng ngày upload_date**

		---

		📦 KẾT QUẢ TRẢ VỀ THEO ĐỊNH DẠNG JSON:
		{{
		"data": [
			{{
			"title": "[Tiêu đề sáng tạo, có hook, không trùng tiêu đề video, làm nổi bật đặc trưng của {product_name}, không đề cập chuyên gia công nghệ]",
			"intro": "[200–300 từ: Giới thiệu hấp dẫn về {product_name}, giới thiệu mục tiêu bài viết, tên các reviewer (không dùng từ "chuyên gia"), đối tượng phù hợp]",
			"features": "[250–300 từ: Tổng hợp tính năng từ tất cả reviewer, ghi rõ trích dẫn]",
			"pros": [
				"[Mỗi ưu điểm là 1 đoạn 3–4 câu. Nếu có yếu tố so sánh thì giữ nguyên cụm so sánh và tách thành câu riêng trong đoạn không được gộp chung 1 câu, và PHẢI trích dẫn nguồn đầy đủ]",
				"[...] (toàn bộ pros, không bỏ sót)",
			],
			"cons": [
				"[Mỗi nhược điểm là 1 đoạn 3–4 câu. Nếu có yếu tố so sánh thì giữ nguyên cụm so sánh và viết thành câu riêng trong đoạn không được gộp chung 1 câu, và PHẢI trích dẫn nguồn đầy đủ]",
				"[...] (toàn bộ cons, không bỏ sót)",
			],
			"price_analysis": "[200–300 từ: Phân tích giá theo từng reviewer, nêu rõ lý do chênh lệch nếu có]",
			"suggestion": "[300–400 từ: Tổng hợp khuyến nghị, chia nhóm người dùng. Nếu có đề cập đến sản phẩm khác thì cũng phải ghi sản phẩm đó vào review, không bỏ sót bất kì recommendation nào của các reviewer dù là nhỏ nhất]"
			}}
		]
		}}

		---

		🧾 CHECKLIST TRƯỚC KHI TRẢ KẾT QUẢ:
		- ✅ Đã liệt kê đầy đủ toàn bộ reviewer
		- ✅ Không thiếu bất kỳ pros/cons/features/recommendation nào
		- ✅ Mỗi đoạn 1 ý duy nhất, có trích dẫn chuẩn
		- ✅ Các ý có yếu tố so sánh phải viết riêng và ghi rõ tên sản phẩm khác
		- ✅ Không lặp “Theo [Author]” quá 3 lần
		- ✅ Tổng độ dài toàn bài: 1000–2000 từ
		- ✅ MỖI Ý KIẾN PHẢI CÓ TRÍCH DẪN ĐẦY ĐỦ theo format: **[url - author đăng ngày upload_date]**

		- ✅ Đảm bảo đúng format JSON như trên (có dấu phẩy đúng sau mỗi phần tử, không bị thiếu hoặc thừa)
		- Nếu response cuối cùng THIẾU bất kỳ thông tin so sánh nào được liệt kê ở đầu (đặc biệt là pros/cons/suggestion) → Đó là LỖI NGHIÊM TRỌNG và phải làm lại!
		🔍 KIỂM TRA CUỐI CÙNG:
		Trước khi trả về, hãy đọc lại toàn bộ JSON và đảm bảo:
		1. Tất cả dấu ngoặc kép được đóng đúng
		2. Tất cả thuộc tính có dấu phẩy (trừ thuộc tính cuối)  
		3. Không có ký tự đặc biệt làm hỏng JSON

		LƯU Ý:
		1. Bài review hay, thực tế, mang lại lợi ích cho người đọc = bài có chứa tên sản phẩm khác được so sánh (iPhone 15 Pro Max, Samsung Galaxy S25, v.v.) để người đọc có góc nhìn khách quan hơn → PHẢI GIỮ NGUYÊN
		2. Mỗi ý kiến PHẢI CÓ TRÍCH DẪN ĐẦY ĐỦ theo format [url - author đăng ngày upload_date] (có thể trích dẫn nhiều nếu có nhiều reviewer cùng ý kiến)
		3. Phần pros/cons/suggestions rất quan trọng với người đọc nên cần phải ghi chi tiết (đặc biệt nếu có so sánh với sản phẩm khác thì càng phải ghi rõ)
		3. Kiểm tra kỹ từng câu so với dữ liệu review trước khi hoàn thành
		"""

		# Generate review using LLM
		# review, answer = self.deepseek_handler.generate_review(prompt)
		# review, answer = self.gpt_handler.generate_review(prompt)
		review, answer = self.gemini_handler.generate_review(prompt)

		# Save data for rouge score calculation
		# save_data(question, answer, context)

		return JsonResponse({
			"reviews": review,
			"video_titles": video_title_map
		}, status=200)
