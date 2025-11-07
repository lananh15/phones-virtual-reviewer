from django.shortcuts import render
from .user import UserViews

class HomeView(UserViews):
	def get_all_categories(self):
		"""
		Retrieves all distinct product categories from the Neo4j database
		Output:
			list: A list of category names (strings)
		"""

		category_query = """
		MATCH (p:Product)
		WHERE p.category IS NOT NULL AND trim(p.category) <> ""
		RETURN DISTINCT p.category AS category
		ORDER BY category
		"""

		with self.neo4j_handler as db:
			categories = db.run_read_query(category_query)

		category_list = [c["category"] for c in categories]

		return category_list

	def get_products_by_category(self, category=None):
		"""
		Retrieves products filtered by category (if provided), including general info
		Inputs:
			category (str, optional): The category to filter by
		Output:
			list: A list of product dictionaries with name, slug, image, and price
		"""

		if category:
			query = """
			MATCH (p:Product)
			WHERE p.category = $category AND p.slug IS NOT NULL AND trim(p.slug) <> ""
			OPTIONAL MATCH (p)-[:HAS_GENERAL_INFO]->(g)
			RETURN p.name AS name, p.slug AS slug, g.image AS image, g.price AS price
			"""
			params = {"category": category}
		else:
			query = """
			MATCH (p:Product)
			WHERE p.slug IS NOT NULL AND trim(p.slug) <> ""
			OPTIONAL MATCH (p)-[:HAS_GENERAL_INFO]->(g)
			RETURN p.name AS name, p.slug AS slug, g.image AS image, g.price AS price
			"""
			params = {}

		with self.neo4j_handler as db:
			result = db.run_read_query(query, params)

		return [dict(record) for record in result]    
	
	def get(self, request):
		"""
		Handles GET requests to the homepage:
			- Retrieves selected category from query parameters
			- Loads all categories and products
			- Renders homepage or 404 if no products found
		Inputs:
			request (HttpRequest): The incoming HTTP request
		Output:
			HttpResponse: Rendered HTML page
		"""

		selected_category = request.GET.get("category")

		categories = self.get_all_categories()
		products = self.get_products_by_category(selected_category)

		context = {
			'products': products,
			'categories': categories,
			"selected_category": selected_category
		}

		if not products:
			return render(request, '404.html')

		return render(request, 'home.html', context)

class ProductDetailView(UserViews):
	def get_product_data(self, slug):
		"""
		Retrieves detailed product data from Neo4j based on slug
		Inputs:
			slug (str): The unique slug identifier of the product
		Output:
			dict or None: Product data dictionary or None if not found
		"""

		query = """ 
		MATCH (p:Product {slug: $slug})
		OPTIONAL MATCH (p)-[:HAS_GENERAL_INFO]->(g)

		OPTIONAL MATCH (p)-[:HAS_HARDWARE]->(chipset:HardwareSpec {key: "chipset"})
		OPTIONAL MATCH (p)-[:HAS_HARDWARE]->(cpu:HardwareSpec {key: "cpu"})
		OPTIONAL MATCH (p)-[:HAS_HARDWARE]->(ram:HardwareSpec {key: "ram"})
		OPTIONAL MATCH (p)-[:HAS_HARDWARE]->(storage:HardwareSpec {key: "storage"})
		OPTIONAL MATCH (p)-[:HAS_HARDWARE]->(battery:HardwareSpec {key: "battery"})
		OPTIONAL MATCH (p)-[:HAS_HARDWARE]->(sim:HardwareSpec {key: "sim"})
		OPTIONAL MATCH (p)-[:HAS_HARDWARE]->(nfc:HardwareSpec {key: "nfc"})

		OPTIONAL MATCH (p)-[:HAS_SOFTWARE]->(s)

		OPTIONAL MATCH (p)-[:HAS_CAMERA]->(rear:CameraSpec {type: "rear"})
		OPTIONAL MATCH (p)-[:HAS_CAMERA]->(front:CameraSpec {type: "front"})

		OPTIONAL MATCH (p)-[:HAS_DISPLAY]->(d)
		OPTIONAL MATCH (p)-[:HAS_DISPLAY_FEATURE]->(df:DisplayFeature)

		RETURN
			p.name AS canonical_name,
			p.slug AS slug,
			p.category AS category,

			g.model AS model,
			g.link AS link,
			g.price AS price,
			g.image AS image,

			chipset.value AS chipset,
			cpu.value AS cpu,
			ram.value AS ram,
			storage.value AS storage,
			battery.value AS battery,
			sim.value AS sim,
			nfc.value AS nfc,

			s.os AS os,

			rear.detail AS rear_camera,
			front.detail AS front_camera,

			d.technology AS display_technology,
			d.size AS display_size,
			d.resolution AS display_resolution,
			collect(df.text) AS display_features
		"""

		with self.neo4j_handler as db:
			result = db.run_read_query(query, {"slug": slug})

		return dict(result[0]) if result else None
	
	def generate_titles(self, product):
		"""
		Formats product attributes into labeled tuples for display
		Inputs:
			product (dict): Product data dictionary
		Output:
			list: A list of (label, value) tuples for display
		"""

		return [
			("Chipset", product.get("chipset")),
			("CPU", product.get("cpu")),
			("RAM", product.get("ram")),
			("Bộ nhớ trong", product.get("storage")),
			("Pin", product.get("battery")),
			("SIM", product.get("sim")),
			("Hỗ trợ NFC", "Có" if product.get("nfc") in ["true", "True", "1", True] else "Không"),
			("Hệ điều hành", product.get("os")),
			("Camera trước", product.get("front_camera")),
			("Camera sau", product.get("rear_camera")),
			("Công nghệ màn hình", product.get("display_technology")),
			("Kích thước màn hình", product.get("display_size")),
			("Độ phân giải", product.get("display_resolution")),
			("Tính năng màn hình", "\n".join(product.get("display_features", []))),
		]
	
	def get(self, request, **kwargs):
		"""
        Handles GET requests to the product detail page:
            - Retrieves product data by slug
            - Generates display titles
            - Renders detail page or 404 if product not found
        Inputs:
            request (HttpRequest): The incoming HTTP request
            kwargs (dict): URL parameters including 'slug'
        Output:
            HttpResponse: Rendered HTML page
        """

		slug = kwargs.get('slug')
		product = self.get_product_data(slug)

		if not product:
			return render(request, '404.html')

		titles = self.generate_titles(product)

		context = {
			'product': product,
			'titles': titles,
		}

		return render(request, 'product_detail.html', context)