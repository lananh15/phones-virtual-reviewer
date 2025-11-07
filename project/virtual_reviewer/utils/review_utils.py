import re

def get_context(reviewers, product_info):
	"""
	Generates context strings from specifications and reviewer feedback
	Inputs:
		reviewers (list): A list of dictionaries containing reviewer data
		product_info (dict): A dictionary containing product specifications
	Output:
		list: A list of formatted context strings
	"""

	contexts = []
	nsx_parts = []

	model = product_info.get("model")
	price = product_info.get("nsx_price")
	os = product_info.get("os")
	nfc = product_info.get("nfc_support")
	hardware = product_info.get("hardware_specs", [])
	camera = product_info.get("camera_specs", [])
	display = product_info.get("display_features", [])
	display_tech = product_info.get("display_tech")
	display_size = product_info.get("display_size")
	display_res = product_info.get("display_resolution")

	if model:
		nsx_parts.append(f"Mẫu máy: {model}")
	if price:
		nsx_parts.append(f"Giá hiện tại: {price}")
	if os:
		nsx_parts.append(f"Hệ điều hành: {os}")
	if nfc:
		nsx_parts.append(f"Hỗ trợ NFC: {nfc}")
	if hardware:
		nsx_parts.append("Thông số phần cứng: " + ", ".join(hardware))
	if camera:
		nsx_parts.append("Camera: " + ", ".join(camera))
	if display_tech or display_size or display_res:
		disp_desc = f"Màn hình: {display_tech or ''} {display_size or ''} {display_res or ''}".strip()
		nsx_parts.append(disp_desc)
	if display:
		nsx_parts.append("Tính năng màn hình: " + ", ".join(display))
	contexts.append("Thông tin từ nhà sản xuất: " + " | ".join(nsx_parts))

	for r in reviewers:
		author = r.get("author", "Unknown")
		upload_date = r.get("upload_date", "")
		video_url = r.get("url", "")
		title = r.get("title", "")
		pros = r.get("pros", [])
		cons = r.get("cons", [])
		features = r.get("features", [])
		recommendation = r.get("recommendation", "")
		price = r.get("price", "")
		
		context_parts = [f"Reviewer: {author} | Video: {title} ({video_url}) | Ngày đăng: {upload_date}"]

		if pros:
			context_parts.append(f"Ưu điểm từ {author}: " + ", ".join(pros))
		if cons:
			context_parts.append(f"Nhược điểm từ {author}: " + ", ".join(cons))
		if features:
			context_parts.append(f"Tính năng từ {author}: " + ", ".join(features))
		if recommendation:
			context_parts.append(f"Khuyến nghị từ {author}: " + recommendation)
		if price:
			context_parts.append(f"Giá từ {author}: " + price)
		
		contexts.append(" | ".join(context_parts))

	return contexts

def get_answer(review_data):
	"""
	Builds a formatted review summary from structured review data
	Inputs:
		review_data (dict): A dictionary containing structured review components
	Output:
		str: A formatted string summarizing the review
	"""

	return (
		"Giới thiệu: " + review_data["intro"] + "\n\n" +
		"Tính năng nổi bật: " + review_data["features"] + "\n\n" +
		"\nƯu điểm: ".join(review_data["pros"]) + "\n\n" +
		"\nNhược điểm: ".join(review_data["cons"]) + "\n\n" +
		"Giá theo review: " + review_data["price_analysis"] + "\n\n" +
		"Gợi ý phù hợp: " + review_data["suggestion"]
	)

def get_unique_reviewers(reviewers):
	"""
	Filters reviewers to return only unique authors
	Inputs:
		reviewers (list): A list of reviewer dictionaries
	Output:
		list: A list of unique reviewer dictionaries
	"""

	unique = {}

	for r in reviewers:
		name = r.get('author', 'Unknown')

		if name not in unique:
			unique[name] = r

	return list(unique.values())

# Cleans a JSON-formatted string by removing markdown wrappers
def clean_json_response(response: str) -> str:
	"""
	Cleans a JSON-formatted string by removing markdown wrappers
	Inputs:
		response (str): A string containing JSON wrapped in markdown formatting
	Output:
		str: A cleaned JSON string
	"""

	response = response.strip()

	if response.startswith("```json"):
		response = response[7:].strip()
	elif response.startswith("```"):
		response = response[3:].strip()

	if response.endswith("```"):
		response = response[:-3].strip()

	match = re.search(r"\{[\s\S]*\}", response)

	if match:
		return match.group(0).strip()

	return response