from django.views import View
from django.shortcuts import render
from django.utils.text import slugify
from ..services.neo4j_handler import Neo4jHandler
from ..services.gpt_handler import GPTHandler
from ..services.gemini_handler import GeminiHandler
from ..services.deepseek_handler import DeepSeekHandler
from django.views import View
from django.shortcuts import render
from django.utils.text import slugify

class UserViews(View):
	def dispatch(self, request, *args, **kwargs):
		"""
		Overrides the dispatch method to initialize service handlers before handling the request
		Inputs:
			request (HttpRequest): The incoming HTTP request
			*args, **kwargs: Additional arguments passed to the view
		Output:
			HttpResponse: The response returned by the appropriate HTTP method handler
		"""

		self.initialize_handlers()
		response = super().dispatch(request, *args, **kwargs)

		return response
	
	def initialize_handlers(self):
		self.neo4j_handler = Neo4jHandler()
		self.gpt_handler = GPTHandler()
		self.gemini_handler = GeminiHandler()
		self.deepseek_handler = DeepSeekHandler()

		return
		
class CompareView(UserViews):
	def get(self, request):
		"""
		Handles GET requests to the comparison page
		Inputs:
			request (HttpRequest): The incoming HTTP request
		Output:
			HttpResponse: Rendered comparison page
		"""

		return render(request, 'compare.html')
	
class GuideView(UserViews):
	def get(self, request):
		"""
		Handles GET requests to the guide page
		Inputs:
			request (HttpRequest): The incoming HTTP request
		Output:
			HttpResponse: Rendered guide page
		"""

		return render(request, 'guide.html')
		
class AboutView(UserViews):
	def get(self, request):
		"""
		Handles GET requests to the about page
		Inputs:
			request (HttpRequest): The incoming HTTP request
		Output:
			HttpResponse: Rendered about page
		"""

		return render(request, 'about.html')

class SearchView(UserViews):
	def get(self, request):
		"""
		Handles GET requests for product search
			- Retrieves the search keyword from query parameters
			- Executes a Neo4j query to find matching products
			- Renders the search results page
		Inputs:
			request (HttpRequest): The incoming HTTP request
		Output:
			HttpResponse: Rendered search results page
		"""

		keyword_input = request.GET.get("q", "").strip()
		keyword = slugify(keyword_input)

		query = """
		MATCH (p:Product)-[:HAS_GENERAL_INFO]->(g)
		WHERE toLower(p.slug) CONTAINS toLower($keyword)
		AND p.slug IS NOT NULL AND trim(p.slug) <> ""
		RETURN p.name AS name, g.price AS price, g.image AS image, p.slug AS slug
		ORDER BY p.name
		"""

		with self.neo4j_handler as db:
			result = db.run_read_query(query, {"keyword": keyword})

		products = [dict(record) for record in result]
		context = {
			"products": products,
			"keyword": keyword_input,
		}

		return render(request, "search.html", context)