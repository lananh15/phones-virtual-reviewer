from django.views import View
from django.shortcuts import render
from django.utils.text import slugify
from ..services.neo4j_handler import Neo4jHandler
from ..services.gpt_handler import GPTHandler
from django.views import View
from django.shortcuts import render
from django.utils.text import slugify

class UserViews(View):
    def dispatch(self, request, *args, **kwargs):
        self.initialize_handlers()
        response = super().dispatch(request, *args, **kwargs)
        return response
    
    def initialize_handlers(self):
        self.neo4j_handler = Neo4jHandler()
        self.gpt_handler = GPTHandler()
        return
        
class CompareView(UserViews):
    def get(self, request):
        return render(request, 'compare.html')
    
class GuideView(UserViews):
    def get(self, request):
        return render(request, 'guide.html')
        
class AboutView(UserViews):
    def get(self, request):
        return render(request, 'about.html')

class SearchView(UserViews):
    def get(self, request):
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