import requests
import re
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

class InternalLinkRecommender:
    def __init__(self):
        # Modelo para embeddings en español
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.posts_cache = []
        self.embeddings_cache = None
        
    def load_posts_from_wordpress(self, wp_url: str, wp_user: str, wp_password: str) -> List[Dict]:
        """Carga todos los posts de WordPress"""
        all_posts = []
        page = 1
        
        while True:
            try:
                response = requests.get(
                    f"{wp_url}/wp-json/wp/v2/posts",
                    params={
                        "page": page,
                        "per_page": 100,
                        "_fields": "id,title,content,link,slug,excerpt"
                    },
                    auth=(wp_user, wp_password),
                    timeout=15
                )
                
                if response.status_code != 200:
                    break
                    
                posts = response.json()
                if not posts:
                    break
                
                for post in posts:
                    all_posts.append({
                        "id": post["id"],
                        "title": post["title"]["rendered"],
                        "url": post["link"],
                        "slug": post["slug"],
                        "content": self.clean_html(post["content"]["rendered"]),
                        "excerpt": self.clean_html(post["excerpt"]["rendered"]) if post["excerpt"] else ""
                    })
                
                page += 1
                
            except Exception as e:
                print(f"Error loading posts: {e}")
                break
        
        self.posts_cache = all_posts
        return all_posts
    
    def clean_html(self, html: str) -> str:
        """Limpia HTML para obtener texto puro"""
        # Simple HTML tag removal
        clean = re.sub(r'<[^>]+>', ' ', html)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    def generate_embeddings(self, posts: List[Dict]) -> np.ndarray:
        """Genera embeddings para todos los posts"""
        texts = [f"{p['title']} {p['excerpt']} {p['content'][:500]}" for p in posts]
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        self.embeddings_cache = embeddings
        return embeddings
    
    def find_related_posts(self, new_content: str, top_n: int = 5) -> List[Dict]:
        """Encuentra posts relacionados para enlazar"""
        if not self.posts_cache:
            return []
        
        # Generar embedding del nuevo contenido
        new_embedding = self.model.encode([new_content], convert_to_tensor=False)
        
        if self.embeddings_cache is None:
            self.generate_embeddings(self.posts_cache)
        
        # Calcular similitudes
        similarities = cosine_similarity(new_embedding, self.embeddings_cache)[0]
        
        # Obtener índices ordenados por similitud
        sorted_indices = np.argsort(similarities)[::-1]
        
        # Preparar resultados
        results = []
        for idx in sorted_indices[:top_n]:
            if similarities[idx] > 0.3:  # Umbral mínimo
                post = self.posts_cache[idx]
                results.append({
                    "post_id": post["id"],
                    "title": post["title"],
                    "url": post["url"],
                    "similarity": float(similarities[idx]),
                    "suggested_anchor": self.suggest_anchor_text(post["title"], new_content),
                    "reason": self.generate_link_reason(post, similarities[idx])
                })
        
        return results
    
    def suggest_anchor_text(self, post_title: str, new_content: str) -> str:
        """Sugiere texto anchor para el enlace"""
        # Extraer palabras clave del título del post
        words = re.findall(r'\b\w{4,}\b', post_title.lower())
        
        # Buscar coincidencias en el nuevo contenido
        for word in words:
            if word in new_content.lower():
                return word.capitalize()
        
        # Si no hay coincidencia, usar primeras palabras del título
        return post_title[:30] + ("..." if len(post_title) > 30 else "")
    
    def generate_link_reason(self, post: Dict, similarity: float) -> str:
        """Genera una razón para el enlace sugerido"""
        if similarity > 0.7:
            return "Muy relacionado temáticamente"
        elif similarity > 0.5:
            return "Tema complementario"
        elif similarity > 0.3:
            return "Contexto relevante"
        else:
            return "Referencia general"
    
    def generate_link_suggestions(self, title: str, content: str) -> Dict:
        """Genera sugerencias completas de enlazado"""
        # Extraer entidades y conceptos clave
        entities = self.extract_key_entities(content)
        
        # Buscar posts relacionados
        related_posts = self.find_related_posts(f"{title} {content}")
        
        # Categorizar enlaces
        categorized_links = {
            "high_priority": [],  # Similitud > 0.7
            "medium_priority": [],  # Similitud 0.5-0.7
            "low_priority": [],  # Similitud 0.3-0.5
            "contextual": []  # Basado en entidades
        }
        
        for post in related_posts:
            if post["similarity"] > 0.7:
                categorized_links["high_priority"].append(post)
            elif post["similarity"] > 0.5:
                categorized_links["medium_priority"].append(post)
            else:
                categorized_links["low_priority"].append(post)
        
        # Añadir enlaces contextuales basados en entidades
        for entity in entities[:3]:
            entity_posts = self.find_posts_by_entity(entity)
            categorized_links["contextual"].extend(entity_posts[:2])
        
        return categorized_links
    
    def extract_key_entities(self, text: str) -> List[str]:
        """Extrae entidades clave del texto"""
        # Simple entity extraction (en producción usar NER)
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        # Filtrar palabras comunes
        common_words = {"El", "La", "Los", "Las", "Un", "Una", "Para", "Con", "Por"}
        entities = [w for w in words if w not in common_words]
        return list(set(entities))[:10]
    
    def find_posts_by_entity(self, entity: str) -> List[Dict]:
        """Busca posts que mencionen una entidad específica"""
        results = []
        for post in self.posts_cache:
            content_lower = f"{post['title']} {post['excerpt']}".lower()
            if entity.lower() in content_lower:
                results.append({
                    "post_id": post["id"],
                    "title": post["title"],
                    "url": post["url"],
                    "similarity": 0.4,  # Similaridad estimada
                    "suggested_anchor": entity,
                    "reason": f"Menciona '{entity}'"
                })
        return results

# Instancia global
link_recommender = InternalLinkRecommender()
