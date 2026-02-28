from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import requests
import os
from dotenv import load_dotenv
from trending_analyzer import TrendingTopicsAnalyzer
from datetime import datetime

load_dotenv()

app = FastAPI(title="Content AI with Real Categories", version="4.1")

# Inicializar analizador
trends_analyzer = TrendingTopicsAnalyzer()

class PostAnalysis(BaseModel):
    title: str
    content: str
    post_id: Optional[int] = None

class TrendRequest(BaseModel):
    num_recommendations: Optional[int] = 5

# Endpoints existentes
@app.get("/")
async def root():
    return {
        "message": "✅ Content AI API v4.1 con categorías reales",
        "status": "active",
        "your_categories": trends_analyzer.your_blog_categories,
        "endpoints": [
            "/", "/health", "/api/test-wordpress", 
            "/api/analyze-with-links", "/api/trending-topics",
            "/api/content-recommendations", "/api/quick-recommendations",
            "/api/your-categories"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "version": "4.1",
        "categories_loaded": len(trends_analyzer.your_blog_categories)
    }

@app.get("/api/your-categories")
async def get_your_categories():
    """Devuelve las categorías extraídas de tu WordPress"""
    coverage = trends_analyzer.analyze_your_blog_coverage()
    
    return {
        "success": True,
        "categories": trends_analyzer.your_blog_categories,
        "coverage": coverage,
        "summary": {
            "total_categories": len(trends_analyzer.your_blog_categories),
            "total_posts_estimated": sum(coverage.values()),
            "most_covered": max(coverage, key=coverage.get) if coverage else "N/A",
            "least_covered": min(coverage, key=coverage.get) if coverage else "N/A"
        }
    }

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
        return {"success": False, "message": f"Error: {str(e)}"}

# Análisis con enlaces
@app.post("/api/analyze-with-links")
async def analyze_with_links(post: PostAnalysis):
    title_lower = post.title.lower()
    content_lower = post.content.lower()
    
    common_phrases = ["guía completa", "todo sobre", "qué es", "cómo hacer"]
    is_common = any(phrase in title_lower for phrase in common_phrases)
    
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
            "similarity": 0.72,
            "suggested_anchor": "algoritmos discriminadores",
            "reason": "Contenido técnico relacionado",
            "priority": "medium_priority"
        }
    ]
    
    # Lógica simplificada de análisis
    analysis_result = {
        "originality_score": 0.82,
        "classification": "✅ ORIGINAL",
        "common_phrases_detected": is_common,
        "internal_links_suggested": example_links,
        "recommendations": [
            "Añadir más datos específicos",
            "Considerar incluir casos de estudio",
            "Podrías enlazar a posts anteriores para dar contexto"
        ],
        "similar_posts_found": len(example_links),
        "seo_suggestions": [
            "Añadir subtítulos H2 y H3",
            "Incluir al menos 3 imágenes relevantes",
            "Optimizar meta descripción"
        ]
    }
    
    return {
        "success": True,
        "analysis": analysis_result,
        "processed_at": datetime.now().isoformat()
    }

@app.get("/api/trending-topics")
async def get_trending_topics():
    """Devuelve temas trending filtrados por tus categorías"""
    try:
        google_trends = trends_analyzer.get_google_trends()
        twitter_trends = trends_analyzer.get_twitter_trends()
        
        # Calcular stats generales
        total_trends = len(google_trends) + len(twitter_trends)
        
        return {
            "success": True,
            "google_trends": google_trends,
            "twitter_trends": twitter_trends,
            "stats": {
                "total_trends": total_trends,
                "categories_covered": len(set([t["topic"] for t in google_trends])),
                "time_generated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/content-recommendations")
async def get_content_recommendations(request: TrendRequest):
    """Genera recomendaciones personalizadas basadas en tendencias y tu blog"""
    try:
        recommendations = trends_analyzer.generate_content_recommendations(
            num_recommendations=request.num_recommendations
        )
        
        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/quick-recommendations")
async def get_quick_recommendations():
    """Devuelve 3 recomendaciones rápidas para hoy"""
    try:
        recommendations = trends_analyzer.generate_content_recommendations(3)
        
        # Formatear para calendarización
        calendar_items = []
        days = ["Hoy", "Mañana", "Pasado mañana"]
        
        for i, rec in enumerate(recommendations[:3]):
            calendar_items.append({
                "date_offset": i,
                "date_label": days[i] if i < 3 else f"Día {i+1}",
                "recommendation": rec,
                "estimated_time": "2-3 horas",
                "priority": "Alta" if i == 0 else "Media"
            })
        
        return {
            "success": True,
            "quick_calendar": calendar_items,
            "message": f"🎯 {len(calendar_items)} ideas para los próximos días"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
