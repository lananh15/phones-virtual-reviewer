from dotenv import load_dotenv
from neo4j import GraphDatabase
import json
import os

load_dotenv()
# Neo4j Aura info
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASS = os.getenv('NEO4J_PASS')

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def create_data(tx, product_name, entry):
	"""
    Pushes YouTube review data into the Neo4j graph database:
        - Creates nodes for Source ("YoutubeReview"), Product, Video, and VideoReview
        - Links Product to Source and VideoReview
        - Links VideoReview to Video
        - Attaches features, pros, and cons to the VideoReview node
    Inputs:
        tx (neo4j.Transaction): Active Neo4j transaction object
        product_name (str): Name of the product being reviewed
        entry (dict): Dictionary containing video metadata and review content
    Output:
        None (writes data to Neo4j)
    """

	# Create Source Node "YoutubeReview"
	tx.run("""
		MERGE (src:Source {name: "YoutubeReview"})
	""")

	# Create Product + link to Source
	tx.run("""
		MERGE (p:Product {name: $product_name})
		MERGE (src:Source {name: "YoutubeReview"})
		MERGE (src)-[:INCLUDES]->(p)
	""", {"product_name": product_name})

	# Create Video
	tx.run("""
		MERGE (v:Video {video_id: $video_id})
		ON CREATE SET v.title = $video_title,
					  v.url = $video_url,
					  v.author = $video_author,
					  v.upload_date = $upload_date
	""", {
		"video_id": entry["video_id"],
		"video_title": entry["video_title"],
		"video_url": entry["video_url"],
		"video_author": entry["video_author"],
		"upload_date": entry["upload_date"],
	})

	# Create an intermediary node VideoReview
	tx.run("""
		MERGE (review:VideoReview {
			video_id: $video_id,
			product_name: $product_name
		})
		SET review.type = $type,
			review.price = $price,
			review.recommendation = $recommendation

		MERGE (p:Product {name: $product_name})
		MERGE (v:Video {video_id: $video_id})
		MERGE (p)-[:MENTIONED_IN]->(review)
		MERGE (review)-[:IN_VIDEO]->(v)
	""", {
		"product_name": product_name,
		"video_id": entry["video_id"],
		"price": entry.get("price", ""),
		"recommendation": entry.get("recommendation", ""),
		"type": entry.get("type", "")
	})

	# Features → attach to review (not video)
	for feat in entry.get("features", []):
		tx.run("""
			MERGE (f:Feature {text: $text})
			MERGE (r:VideoReview {video_id: $video_id, product_name: $product_name})
			MERGE (r)-[:HAS_FEATURE]->(f)
		""", {"video_id": entry["video_id"], "product_name": product_name, "text": feat})

	for pro in entry.get("pros", []):
		tx.run("""
			MERGE (pr:Pro {text: $text})
			MERGE (r:VideoReview {video_id: $video_id, product_name: $product_name})
			MERGE (r)-[:HAS_PRO]->(pr)
		""", {"video_id": entry["video_id"], "product_name": product_name, "text": pro})

	for con in entry.get("cons", []):
		tx.run("""
			MERGE (c:Con {text: $text})
			MERGE (r:VideoReview {video_id: $video_id, product_name: $product_name})
			MERGE (r)-[:HAS_CON]->(c)
		""", {"video_id": entry["video_id"], "product_name": product_name, "text": con})

"""---------------- Push data from manufacturer (phones_data.json) ----------------"""

def create_manufacturer_data(tx, product):
	"""
    Pushes manufacturer product data into the Neo4j graph database:
        - Creates nodes for Source ("Manufacturer"), Product, and associated specs
        - Links Product to Source and attaches general info, hardware, software, camera, and display specs
        - Ensures all nodes are created or merged to avoid duplication
    Inputs:
        tx (neo4j.Transaction): Active Neo4j transaction object
        product (dict): Dictionary containing structured product data from manufacturer
    Output:
        None (writes data to Neo4j)
    """

	canonical_name = product["canonical_name"]
	slug = product["slug"]
	category = product.get("category", "")

	# Create a parent node for the manufacturer source
	tx.run("""
		MERGE (src:Source {name: "Manufacturer"})
	""")

	# Create a Product node if it doesn’t exist, or attach to it if it already exists
	tx.run("""
		MERGE (p:Product {name: $canonical_name, slug: $slug, category: $category})
		MERGE (src:Source {name: "Manufacturer"})
		MERGE (src)-[:INCLUDES]->(p)
	""", {"canonical_name": canonical_name, "slug": slug, "category": product.get("category")})

	# General Info
	general = product.get("general", {})

	if general:
		tx.run("""
			MERGE (g:GeneralInfo {model: $model, link: $link, price: $price, image: $image})
			MERGE (p:Product {name: $canonical_name})
			MERGE (p)-[:HAS_GENERAL_INFO]->(g)
		""", {
			"canonical_name": canonical_name,
			"model": general.get("model", ""),
			"link": general.get("link", ""),
			"price": general.get("price", ""),
			"image": general.get("image", "")
		})

	# Hardware
	hardware = product.get("hardware", {})

	for key, value in hardware.items():
		if value != "":
			tx.run("""
				MERGE (h:HardwareSpec {key: $key, value: $value})
				MERGE (p:Product {name: $canonical_name})
				MERGE (p)-[:HAS_HARDWARE]->(h)
			""", {"canonical_name": canonical_name, "key": key, "value": str(value)})

	# Software
	software = product.get("software", {})

	if software.get("os"):
		tx.run("""
			MERGE (s:SoftwareSpec {os: $os})
			MERGE (p:Product {name: $canonical_name})
			MERGE (p)-[:HAS_SOFTWARE]->(s)
		""", {"canonical_name": canonical_name, "os": software["os"]})

	# Camera
	camera = product.get("camera", {})

	for cam_type, detail in camera.items():
		if detail:
			tx.run("""
				MERGE (c:CameraSpec {type: $type, detail: $detail})
				MERGE (p:Product {name: $canonical_name})
				MERGE (p)-[:HAS_CAMERA]->(c)
			""", {"canonical_name": canonical_name, "type": cam_type, "detail": detail})

	# Display
	display = product.get("display", {})

	if display:
		tx.run("""
			MERGE (d:DisplaySpec {
				technology: $technology,
				size: $size,
				resolution: $resolution
			})
			MERGE (p:Product {name: $canonical_name})
			MERGE (p)-[:HAS_DISPLAY]->(d)
		""", {
			"canonical_name": canonical_name,
			"technology": display.get("technology", ""),
			"size": display.get("size", ""),
			"resolution": display.get("resolution", "")
		})

		for feat in display.get("features", []):
			if feat.strip():
				tx.run("""
					MERGE (df:DisplayFeature {text: $text})
					MERGE (p:Product {name: $canonical_name})
					MERGE (p)-[:HAS_DISPLAY_FEATURE]->(df)
				""", {
					"canonical_name": canonical_name,
					"text": feat
				})

# Load data from phones_data.json
with open("phones_data.json", "r", encoding="utf-8") as f:
	manufacturer_data = json.load(f)

with driver.session() as session:
	for product in manufacturer_data["products"]:
		session.execute_write(create_manufacturer_data, product)

print("🏭 Đã đẩy dữ liệu từ NSX (Manufacturer) lên Neo4j thành công!")

# Load JSON data (merged from many transcript files)
with open("video-youtube/youtube_reviews.json", "r", encoding="utf-8") as f:
	data = json.load(f)

with driver.session() as session:
	for product_name, entries in data["products"].items():
		for entry in entries:
			session.execute_write(create_data, product_name, entry)

print("✅ Đẩy dữ liệu lên Neo4j thành công!")