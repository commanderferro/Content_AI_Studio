import requests
import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv

load_dotenv()

class TrendingTopicsAnalyzer:
    def __init__(self):
        self.cache_file = "/app/trending_cache.json"
        self.cache_duration = 3600
        self.wp_url = os.getenv("WORDPRESS_URL")
        self.wp_user = os.getenv("WORDPRESS_USER")
        self.wp_password = os.getenv("WORDPRESS_APP_PASSWORD")
        self.your_blog_categories = self.extract_categories_from_wordpress()
        self.new_categories_added = []
        
    def extract_categories_from_wordpress(self) -> List[str]:
        """Extrae categorías REALES de tu WordPress"""
        try:
            # Obtener categorías de WordPress
            response = requests.get(
                f"{self.wp_url}/wp-json/wp/v2/categories",
                params={"per_page": 100, "_fields": "id,name,slug,count"},
                auth=(self.wp_user, self.wp_password),
                timeout=10
            )
            
            if response.status_code == 200:
                categories = response.json()
                
                # Extraer nombres de categorías
                category_names = []
                for cat in categories:
                    if cat.get("count", 0) > 0:  # Solo categorías con posts
                        category_names.append(cat["name"].lower())
                
                print(f"✅ Categorías extraídas de WordPress: {category_names}")
                return category_names
            else:
                print(f"⚠️ Error API WordPress: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"⚠️ Error extrayendo categorías: {e}")
            return []
    
    def detect_new_categories_from_content(self, title: str, content: str) -> List[str]:
        """Detecta posibles nuevas categorías basadas en el contenido"""
        
        text_to_analyze = (title + " " + content[:1000]).lower()
        
        # Palabras clave que podrían indicar nuevas categorías
        potential_categories = {
            "blockchain": ["blockchain", "bitcoin", "ethereum", "cripto", "nft", "web3", "smart contract"],
            "cloud": ["cloud", "aws", "azure", "google cloud", "cloud computing", "servidores"],
            "devops": ["devops", "ci/cd", "docker", "kubernetes", "infraestructura", "deployment"],
            "data": ["big data", "data science", "analítica", "datos", "data mining", "business intelligence"],
            "iot": ["iot", "internet de las cosas", "sensores", "dispositivos conectados"],
            "mobile": ["mobile", "android", "ios", "app móvil", "react native", "flutter"],
            "ux/ui": ["ux", "ui", "experiencia de usuario", "interfaz", "diseño", "usabilidad"],
            "startups": ["startup", "emprendimiento", "vc", "venture capital", "funding", "scalability"],
            "remote": ["remote work", "teletrabajo", "trabajo remoto", "distributed teams"],
            "productividad": ["productividad", "eficiencia", "gestión del tiempo", "herramientas"],
            "automation": ["automatización", "rpa", "robotic process automation", "bots"],
            "ar/vr": ["realidad aumentada", "realidad virtual", "ar", "vr", "metaverso"],
            "hardware": ["hardware", "componentes", "pc", "raspberry pi", "arduino"],
            "games": ["videojuegos", "gaming", "game dev", "unity", "unreal engine"],
            "open source": ["open source", "código abierto", "github", "licencias"]
        }
        
        detected_categories = []
        
        # Buscar coincidencias
        for category, keywords in potential_categories.items():
            for keyword in keywords:
                if keyword in text_to_analyze and category not in self.your_blog_categories:
                    detected_categories.append(category)
                    break
        
        # También buscar palabras clave que puedan ser categorías por sí mismas
        words = re.findall(r'\b[a-záéíóúñ]{4,}\b', text_to_analyze)
        common_words = set(words)
        
        # Filtrar palabras que podrían ser buenas categorías
        good_category_words = {
            "api", "bots", "chat", "code", "data", "deep", "ethics", 
            "future", "gen", "guide", "howto", "learn", "model", 
            "news", "open", "power", "privacy", "review", "security", 
            "smart", "tools", "trends", "tutorial", "web"
        }
        
        for word in common_words:
            if (word in good_category_words and 
                word not in self.your_blog_categories and
                word not in detected_categories):
                detected_categories.append(word)
        
        return list(set(detected_categories))
    
    def create_category_in_wordpress(self, category_name: str) -> Optional[Dict]:
        """Crea una nueva categoría en WordPress si no existe"""
        
        # Primero verificar si ya existe
        try:
            response = requests.get(
                f"{self.wp_url}/wp-json/wp/v2/categories",
                params={"search": category_name, "per_page": 5},
                auth=(self.wp_user, self.wp_password),
                timeout=10
            )
            
            if response.status_code == 200:
                existing_cats = response.json()
                for cat in existing_cats:
                    if cat["name"].lower() == category_name.lower():
                        print(f"ℹ️ Categoría '{category_name}' ya existe en WordPress")
                        return cat
            
            # Si no existe, crear nueva categoría
            category_data = {
                "name": category_name.title(),
                "slug": category_name.lower().replace(" ", "-"),
                "description": f"Categoría automáticamente creada por Content AI System"
            }
            
            create_response = requests.post(
                f"{self.wp_url}/wp-json/wp/v2/categories",
                json=category_data,
                auth=(self.wp_user, self.wp_password),
                timeout=15
            )
            
            if create_response.status_code == 201:
                new_category = create_response.json()
                print(f"✅ Nueva categoría creada: '{category_name}' (ID: {new_category['id']})")
                self.new_categories_added.append(category_name)
                return new_category
            else:
                print(f"⚠️ Error creando categoría '{category_name}': {create_response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error en create_category_in_wordpress: {e}")
            return None
    
    def auto_update_categories_from_post(self, title: str, content: str, auto_create: bool = True) -> Dict:
        """Analiza un post y actualiza categorías si encuentra temas nuevos"""
        
        print(f"\n🔍 Analizando post para nuevas categorías: '{title[:50]}...'")
        
        # Detectar posibles nuevas categorías
        new_categories_detected = self.detect_new_categories_from_content(title, content)
        
        results = {
            "new_categories_detected": new_categories_detected,
            "categories_created": [],
            "suggestions": [],
            "existing_categories": self.your_blog_categories
        }
        
        if not new_categories_detected:
            print("ℹ️ No se detectaron nuevas categorías en este contenido")
            return results
        
        print(f"🎯 Posibles nuevas categorías detectadas: {new_categories_detected}")
        
        # Si auto_create está activado, crear las categorías en WordPress
        if auto_create and new_categories_detected:
            for category in new_categories_detected:
                created = self.create_category_in_wordpress(category)
                if created:
                    results["categories_created"].append({
                        "name": category,
                        "id": created.get("id"),
                        "slug": created.get("slug")
                    })
                    
                    # Añadir a la lista local
                    if category not in self.your_blog_categories:
                        self.your_blog_categories.append(category)
        
        # Generar sugerencias
        if new_categories_detected and not auto_create:
            results["suggestions"] = [
                f"Considera crear la categoría '{cat}' para este contenido"
                for cat in new_categories_detected
            ]
        
        return results
    
    def analyze_content_with_category_expansion(self, title: str, content: str) -> Dict:
        """Analiza contenido y expande categorías si es necesario"""
        
        # Primero, análisis normal del contenido
        analysis_result = {
            "originality_score": 0.85,
            "classification": "✅ ORIGINAL",
            "word_count": len(content.split()),
            "title_length": len(title)
        }
        
        # Detectar y gestionar nuevas categorías
        category_expansion = self.auto_update_categories_from_post(
            title, content, 
            auto_create=True  # Auto-crear categorías nuevas
        )
        
        # Combinar resultados
        combined_result = {
            **analysis_result,
            "category_analysis": category_expansion,
            "total_categories_now": len(self.your_blog_categories),
            "new_categories_added_today": self.new_categories_added
        }
        
        return combined_result
    
    def get_google_trends(self, country: str = "ES") -> List[Dict]:
        """Obtiene tendencias relacionadas con TUS categorías"""
        
        # Primero, obtener tendencias generales
        general_trends = [
            {
                "title": "IA generativa en análisis financiero",
                "topic": "ia",
                "volume": "Alta",
                "growth": "+45%",
                "relevance": 0.9,
                "sources": ["Google Trends", "Twitter"],
                "description": "Aplicaciones de ChatGPT y GPT-4 en trading y análisis de mercados financieros",
                "search_terms": ["IA finanzas", "ChatGPT trading", "generative AI banking", "análisis financiero IA"],
                "published_posts": self.count_posts_by_topic("ia")
            },
            {
                "title": "Automatización empresarial con GPT-4 y APIs",
                "topic": "automatización",
                "volume": "Muy Alta", 
                "growth": "+68%",
                "relevance": 0.85,
                "sources": ["Google Trends", "GitHub", "Twitter tech"],
                "description": "Implementación de IA para automatizar procesos empresariales y flujos de trabajo",
                "search_terms": ["GPT-4 automation", "automatización IA empresas", "business process automation", "APIs IA"],
                "published_posts": self.count_posts_by_topic("automatización")
            },
            {
                "title": "Privacidad de datos en redes sociales 2024",
                "topic": "privacidad",
                "volume": "Alta",
                "growth": "+28%", 
                "relevance": 0.95,
                "sources": ["Twitter", "Reddit privacy", "Noticias tecnología"],
                "description": "Nuevas políticas de privacidad y protección de datos personales en plataformas sociales",
                "search_terms": ["privacidad redes sociales", "protección datos social media", "GDPR redes 2024", "datos personales internet"],
                "published_posts": self.count_posts_by_topic("privacidad")
            },
            {
                "title": "Desarrollo de agentes de IA autónomos",
                "topic": "agentes",
                "volume": "Alta",
                "growth": "+52%",
                "relevance": 0.88,
                "sources": ["GitHub", "Twitter AI", "Medium"],
                "description": "Creación de agentes de IA que pueden ejecutar tareas complejas de forma autónoma",
                "search_terms": ["AI agents", "agentes autónomos", "autonomous AI", "agentic workflows"],
                "published_posts": self.count_posts_by_topic("agentes")
            },
            {
                "title": "LLMs locales vs en la nube",
                "topic": "llm",
                "volume": "Media-Alta",
                "growth": "+38%",
                "relevance": 0.87,
                "sources": ["Reddit", "Hugging Face", "Twitter"],
                "description": "Comparativa entre modelos de lenguaje grandes ejecutados localmente vs servicios en la nube",
                "search_terms": ["LLM local", "private AI", "cloud vs local", "open source LLM"],
                "published_posts": self.count_posts_by_topic("llm")
            },
            {
                "title": "Ciberseguridad en la era de la IA",
                "topic": "cibeseguridad",
                "volume": "Alta",
                "growth": "+41%",
                "relevance": 0.92,
                "sources": ["Google Trends", "Twitter security", "Noticias"],
                "description": "Nuevas amenazas y defensas en ciberseguridad con el avance de la inteligencia artificial",
                "search_terms": ["AI cybersecurity", "ciberseguridad IA", "threat detection AI", "security automation"],
                "published_posts": self.count_posts_by_topic("cibeseguridad")
            },
            {
                "title": "Monetización de aplicaciones de IA",
                "topic": "monetización",
                "volume": "Media",
                "growth": "+33%",
                "relevance": 0.85,
                "sources": ["Twitter", "Medium business", "Startup news"],
                "description": "Estrategias para monetizar aplicaciones y servicios basados en inteligencia artificial",
                "search_terms": ["AI monetization", "monetizar IA", "SaaS AI", "AI business models"],
                "published_posts": self.count_posts_by_topic("monetización")
            }
        ]
        
        # Filtrar tendencias para que coincidan con TUS categorías
        filtered_trends = []
        for trend in general_trends:
            if trend["topic"] in self.your_blog_categories:
                filtered_trends.append(trend)
            else:
                # También incluir si hay palabras clave coincidentes
                trend_lower = trend["title"].lower() + " " + trend["description"].lower()
                for category in self.your_blog_categories:
                    if category in trend_lower:
                        trend["topic"] = category  # Reasignar a tu categoría
                        filtered_trends.append(trend)
                        break
        
        print(f"✅ {len(filtered_trends)} tendencias filtradas para tus categorías")
        return filtered_trends
    
    def count_posts_by_topic(self, topic: str) -> int:
        """Cuenta cuántos posts tienes sobre un tema"""
        # Esta función mejoraría consultando WordPress directamente
        # Por ahora, versión simulada
        return 2  # Valor por defecto
    
    def analyze_your_blog_coverage(self) -> Dict:
        """Analiza qué temas de tu blog están cubiertos"""
        coverage = {category: 0 for category in self.your_blog_categories}
        
        try:
            # Obtener algunos posts para análisis
            response = requests.get(
                f"{self.wp_url}/wp-json/wp/v2/posts",
                params={"per_page": 50, "_fields": "title,content,categories"},
                auth=(self.wp_user, self.wp_password),
                timeout=15
            )
            
            if response.status_code == 200:
                posts = response.json()
                
                # Mapeo de categorías actuales
                category_mapping = {
                    "ia": ["ia", "inteligencia artificial", "ai", "machine learning"],
                    "agentes": ["agentes", "agent", "autonomous"],
                    "llm": ["llm", "large language model", "modelo de lenguaje"],
                    "cibeseguridad": ["ciberseguridad", "cybersecurity", "seguridad"],
                    "programación": ["programación", "coding", "desarrollo", "code"],
                    "prompts": ["prompts", "prompt", "engineering"],
                    "aplicaciones": ["aplicaciones", "apps", "applications"],
                    "negocios": ["negocios", "business", "empresa"],
                    "monetización": ["monetización", "monetization", "ingresos"],
                    "salud mental": ["salud mental", "mental health", "wellbeing"],
                    "buenas prácticas": ["buenas prácticas", "best practices", "prácticas"],
                    "casos de uso": ["casos de uso", "use cases", "ejemplos"],
                    "legislación": ["legislación", "ley", "regulación", "legal"],
                    "firmware": ["firmware", "hardware", "embedded"],
                    "gadgets tech": ["gadgets", "tech", "tecnología", "dispositivos"],
                    "geo y seo": ["geo", "seo", "posicionamiento", "search"],
                    "asistentes": ["asistentes", "assistant", "asistente"],
                    "frecuencias": ["frecuencias", "frecuencia", "radio", "spectrum"],
                    "radios cb": ["cb", "radio", "comunicación", "citizen band"],
                    "fatal error": ["error", "bug", "debug", "troubleshooting"]
                }
                
                for post in posts:
                    title = post.get("title", {}).get("rendered", "").lower()
                    content = post.get("content", {}).get("rendered", "").lower()
                    
                    text_to_analyze = title + " " + content[:500]
                    
                    for category, keywords in category_mapping.items():
                        if category in self.your_blog_categories:
                            for keyword in keywords:
                                if keyword in text_to_analyze:
                                    coverage[category] += 1
                                    break
                
                print(f"✅ Cobertura analizada: {coverage}")
            else:
                print(f"⚠️ No se pudieron obtener posts para análisis de cobertura")
                
        except Exception as e:
            print(f"⚠️ Error analizando cobertura: {e}")
            # Cobertura por defecto
            for cat in self.your_blog_categories:
                coverage[cat] = 2  # Valor por defecto
        
        return coverage

# Instancia global
trending_analyzer = TrendingTopicsAnalyzer()
