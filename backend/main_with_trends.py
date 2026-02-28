from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import requests
import os
from dotenv import load_dotenv
from trending_analyzer import TrendingTopicsAnalyzer
import json

load_dotenv()

app = FastAPI(title="Content AI API with Trends", version="4.0")

# Inicializar analizador de tendencias
trends_analyzer = TrendingTopicsAnalyzer()

# Modelos
class PostAnalysis(BaseModel):
    title: str
    content: str
    post_id: Optional[int] = None

class TrendRequest(BaseModel):
    num_recommendations: Optional[int] = 5
    categories_filter: Optional[List[str]] = None

# Endpoints existentes
@app.get("/")
async def root():
    return {
        "message": "✅ Content AI API v4.0 con Trending Topics",
        "status": "active",
        "endpoints": [
            "/", "/health", "/api/test-wordpress", 
            "/api/analyze", "/api/analyze-with-links",
            "/api/trending-topics", "/api/content-recommendations"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "4.0"}

@app.get("/api/test-wordpress")
async def test_wp():
    wp_url = os.getenv("WORDPRESS_URL")
    wp_user = os.getenv("WORDPRESS_USER")
    wp_pass = os.getenv("WORDPRESS_APP_PASSWORD")
    
    try:
        response = requests.get(
            f"{wp_url}/wp-json/wp/v2/posts",
            params={"_fields": "id,title", "per_page": 3},
            auth=(wp_user, wp_pass),
            timeout=10
        )
        
        if response.status_code == 200:
            posts = response.json()
            return {
                "success": True,
                "message": "✅ WordPress conectado",
                "total_posts": len(posts),
                "sample_posts": [
                    {"id": p["id"], "title": p["title"]["rendered"]}
                    for p in posts[:3]
                ]
            }
        else:
            return {"success": False, "message": f"Error: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"})

# Análisis con enlaces (versión simple)
@app.post("/api/analyze-with-links")
async def analyze_with_links(post: PostAnalysis):
    title_lower = post.title.lower()
    content_lower = post.content.lower()
    
    common_phrases = ["guía completa", "todo sobre", "qué es", "cómo hacer"]
    is_common = any(phrase in title_lower for phrase in common_phrases)
    
    # Enlaces de ejemplo basados en posts conocidos
    example_links = [
        {
            "post_id": 784,
            "title": "ETF's de oro para no inversores",
            "url": "https://verifiedhuman.es/?p=784",
            "similarity": 0.85,
            "suggested_anchor": "ETF",
            "reason": "Tema principal coincidente",
            "priority": "high_priority"
        },
        {
            "post_id": 802,
            "title": "Algoritmos que discriminan y modelos que hunden empresas",
            "url": "https://verifiedhuman.es/?p=802",
            "similarity": 0.65,
            "suggested_anchor": "algoritmos",
            "reason": "Conceptos relacionados",
            "priority": "medium_priority"
        },
    ]
    
    relevant_links = example_links
    
    return {
        "is_novel": not is_common,
        "score": 0.8 if not is_common else 0.3,
        "word_count": len(content_lower.split()),
        "internal_links": {
            "total_suggestions": len(relevant_links),
            "suggestions": relevant_links,
            "categories": {
                "high_priority": len([l for l in relevant_links if l["priority"] == "high_priority"]),
                "medium_priority": len([l for l in relevant_links if l["priority"] == "medium_priority"]),
                "low_priority": 0,
                "contextual": 1
            }
        },
        "analysis": {
            "title_too_common": is_common,
            "suggestions": [
                "Considera un título más específico" if is_common else "✅ Título original",
                f"Se encontraron {len(relevant_links)} enlaces relevantes"
            ]
        }
    }

# ========= NUEVOS ENDPOINTS PARA TRENDING TOPICS =========

@app.get("/api/trending-topics")
async def get_trending_topics():
    """Obtiene temas trending de diversas fuentes"""
    try:
        google_trends = trends_analyzer.get_google_trends()
        twitter_trends = trends_analyzer.get_twitter_trends()
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "sources": {
                "google_trends": len(google_trends),
                "twitter_trends": len(twitter_trends)
            },
            "top_trends": google_trends[:5],
            "twitter_trends": twitter_trends[:5]
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/content-recommendations")
async def get_content_recommendations(request: TrendRequest):
    """Genera recomendaciones de contenido basadas en tendencias"""
    try:
        num_recs = request.num_recommendations or 5
        categories = request.categories_filter
        
        recommendations = trends_analyzer.generate_content_recommendations(num_recs)
        
        # Filtrar por categorías si se especifican
        if categories:
            recommendations = [
                rec for rec in recommendations 
                if rec["trend_data"]["topic"] in categories
            ]
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "num_recommendations": len(recommendations),
            "recommendations": recommendations,
            "summary": {
                "by_topic": self._summarize_by_topic(recommendations),
                "by_source": self._summarize_by_source(recommendations),
                "avg_seo_potential": sum(r["estimated_seo_potential"] for r in recommendations) / len(recommendations) if recommendations else 0
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/quick-recommendations")
async def get_quick_recommendations():
    """Recomendaciones rápidas (3-5 temas)"""
    try:
        recommendations = trends_analyzer.generate_content_recommendations(5)
        
        # Formatear para respuesta simple
        simple_recs = []
        for rec in recommendations[:5]:  # Top 5
            simple_recs.append({
                "title": rec["title"],
                "topic": rec["trend_data"]["topic"],
                "why_relevant": rec["why_relevant"],
                "seo_potential": f"{rec['estimated_seo_potential']:.0f}%",
                "priority": "Alta" if rec["estimated_seo_potential"] > 70 else "Media"
            })
        
        return {
            "success": True,
            "message": f"🎯 {len(simple_recs)} recomendaciones generadas",
            "recommendations": simple_recs,
            "action_items": [
                "Elige 1-2 temas para desarrollar esta semana",
                "Investiga cada tema antes de escribir",
                "Planifica enlaces internos a posts existentes"
            ]
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

# Funciones auxiliares
def _summarize_by_topic(recommendations: List[Dict]) -> Dict:
    summary = {}
    for rec in recommendations:
        topic = rec["trend_data"]["topic"]
        summary[topic] = summary.get(topic, 0) + 1
    return summary

def _summarize_by_source(recommendations: List[Dict]) -> Dict:
    summary = {}
    for rec in recommendations:
        source = rec["trend_source"]
        summary[source] = summary.get(source, 0) + 1
    return summary

# Importar datetime aquí
from datetime import datetime

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
