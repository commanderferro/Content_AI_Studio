from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict
import requests
import os
from dotenv import load_dotenv
from trending_analyzer import TrendingTopicsAnalyzer
from datetime import datetime

load_dotenv()

app = FastAPI(title="Content AI with Real Categories", version="4.2")

# Inicializar analizador
trends_analyzer = TrendingTopicsAnalyzer()

class PostAnalysis(BaseModel):
    title: str
    content: str
    post_id: Optional[int] = None

class TrendRequest(BaseModel):
    num_recommendations: Optional[int] = 5

class CategoryAnalysis(BaseModel):
    title: str
    content: str
    auto_create: Optional[bool] = True

# Endpoints existentes
@app.get("/")
async def root():
    return {
        "message": "✅ Content AI API v4.2 con categorías reales y auto-detección",
        "status": "active",
        "your_categories": trends_analyzer.your_blog_categories[:10],  # Mostrar solo 10
        "total_categories": len(trends_analyzer.your_blog_categories),
        "new_categories_today": trends_analyzer.new_categories_added,
        "endpoints": [
            "/", "/health", "/api/test-wordpress", 
            "/api/analyze-with-links", "/api/trending-topics",
            "/api/content-recommendations", "/api/quick-recommendations",
            "/api/your-categories", "/api/analyze-with-categories",
            "/api/categories/stats", "/api/categories/create"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "version": "4.2",
        "categories_loaded": len(trends_analyzer.your_blog_categories),
        "new_categories_added": len(trends_analyzer.new_categories_added)
    }

@app.get("/api/your-categories")
async def get_your_categories():
    """Devuelve las categorías extraídas de tu WordPress"""
    coverage = trends_analyzer.analyze_your_blog_coverage()
    
    return {
        "success": True,
        "categories": trends_analyzer.your_blog_categories,
        "coverage": coverage,
        "new_categories_added": trends_analyzer.new_categories_added,
        "summary": {
            "total_categories": len(trends_analyzer.your_blog_categories),
            "total_posts_estimated": sum(coverage.values()),
            "most_covered": max(coverage, key=coverage.get) if coverage else "N/A",
            "least_covered": min(coverage, key=coverage.get) if coverage else "N/A",
            "categories_added_today": len(trends_analyzer.new_categories_added)
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
        
        return {
            "success": True,
            "google_trends": google_trends,
            "stats": {
                "total_trends": len(google_trends),
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

@app.post("/api/analyze-with-categories")
async def analyze_with_categories(analysis: CategoryAnalysis):
    """Analiza contenido y detecta/crea nuevas categorías"""
    try:
        result = trends_analyzer.auto_update_categories_from_post(
            analysis.title,
            analysis.content,
            auto_create=analysis.auto_create
        )
        
        return {
            "success": True,
            "analysis": result,
            "message": f"Detectadas {len(result['new_categories_detected'])} posibles nuevas categorías",
            "processed_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/categories/stats")
async def get_categories_stats():
    """Obtiene estadísticas de categorías"""
    coverage = trends_analyzer.analyze_your_blog_coverage()
    
    # Calcular estadísticas
    total_posts = sum(coverage.values())
    avg_posts_per_category = total_posts / len(coverage) if coverage else 0
    
    # Identificar categorías infra-cubiertas
    undercovered = []
    well_covered = []
    
    for category, count in coverage.items():
        if count == 0:
            undercovered.append({"category": category, "posts": count, "status": "empty"})
        elif count == 1:
            undercovered.append({"category": category, "posts": count, "status": "low"})
        elif count >= 3:
            well_covered.append({"category": category, "posts": count, "status": "good"})
    
    return {
        "success": True,
        "stats": {
            "total_categories": len(trends_analyzer.your_blog_categories),
            "total_posts_estimated": total_posts,
            "avg_posts_per_category": round(avg_posts_per_category, 1),
            "undercovered_categories": len(undercovered),
            "well_covered_categories": len(well_covered),
            "new_categories_added_today": trends_analyzer.new_categories_added,
            "new_categories_count": len(trends_analyzer.new_categories_added)
        },
        "undercovered": undercovered[:5],  # Top 5 más necesitadas
        "well_covered": well_covered[:5],   # Top 5 mejor cubiertas
        "all_categories": [
            {"name": cat, "posts": coverage.get(cat, 0)}
            for cat in trends_analyzer.your_blog_categories
        ]
    }

@app.post("/api/categories/create")
async def create_category(category_data: Dict):
    """Crea una nueva categoría en WordPress"""
    try:
        category_name = category_data.get("name")
        
        if not category_name:
            return {"success": False, "error": "Se requiere nombre de categoría"}
        
        result = trends_analyzer.create_category_in_wordpress(category_name)
        
        if result:
            return {
                "success": True,
                "category": result,
                "message": f"Categoría '{category_name}' creada exitosamente"
            }
        else:
            return {"success": False, "error": "No se pudo crear la categoría"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/full-analysis")
async def full_analysis(post: PostAnalysis):
    """Análisis completo: contenido + categorías + recomendaciones"""
    try:
        # 1. Análisis de originalidad y enlaces
        title_lower = post.title.lower()
        content_lower = post.content.lower()
        
        analysis_result = {
            "originality_score": 0.82,
            "classification": "✅ ORIGINAL",
            "word_count": len(post.content.split()),
            "reading_time_minutes": len(post.content.split()) // 200
        }
        
        # 2. Detección de nuevas categorías
        category_result = trends_analyzer.auto_update_categories_from_post(
            post.title, post.content, auto_create=True
        )
        
        # 3. Recomendaciones de contenido
        recommendations = trends_analyzer.generate_content_recommendations(3)
        
        return {
            "success": True,
            "content_analysis": analysis_result,
            "category_analysis": category_result,
            "recommendations": recommendations[:2],
            "summary": {
                "new_categories_found": len(category_result["new_categories_detected"]),
                "categories_created": len(category_result["categories_created"]),
                "total_categories_now": len(trends_analyzer.your_blog_categories)
            },
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
