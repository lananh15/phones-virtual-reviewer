from django.http import JsonResponse
from .user import UserViews

class GenerateReviewView(UserViews):
    def get(self, request):
        product_name = request.GET.get("name", "")
        # print(f"🔍 Tạo review cho sản phẩm: {product_name}")
        if not product_name:
            return JsonResponse({"error": "Thiếu tên sản phẩm"}, status=400)

        # Truy vấn Neo4j
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
        with self.neo4j_handler as db:
            result = db.run_read_query(query, {"product_name": product_name})
        
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
        
        review = self.gpt_handler.generate_review(
            product_name=product_name, reviewers=reviewers)

        return JsonResponse({
            "reviews": review,
            "video_titles": video_title_map
        }, status=200)