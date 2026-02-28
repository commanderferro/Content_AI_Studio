import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def sync_posts():
    wp_url = os.getenv("WORDPRESS_URL")
    wp_user = os.getenv("WORDPRESS_USER")
    wp_password = os.getenv("WORDPRESS_APP_PASSWORD")
    
    print(f"🔄 Sincronizando con WordPress: {wp_url}")
    
    # Obtener todos los posts
    all_posts = []
    page = 1
    
    while True:
        response = requests.get(
            f"{wp_url}/wp-json/wp/v2/posts",
            params={
                "page": page,
                "per_page": 100,
                "_fields": "id,title,content,date,link,slug,excerpt"
            },
            auth=(wp_user, wp_password),
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Error en página {page}: {response.status_code}")
            print(f"Continuando con los posts obtenidos...")
            break
            
        posts = response.json()
        if not posts:
            break
            
        all_posts.extend(posts)
        print(f"📥 Página {page}: {len(posts)} posts")
        page += 1
    
    # Guardar en archivo JSON (ruta dentro del contenedor)
    posts_data = []
    for post in all_posts:
        posts_data.append({
            "id": post["id"],
            "title": post["title"]["rendered"],
            "url": post["link"],
            "date": post["date"],
            "excerpt": post["excerpt"]["rendered"] if post["excerpt"] else ""
        })
    
    # Guardar en /app/ (dentro del contenedor backend)
    with open('/app/posts_data.json', 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sincronizados {len(all_posts)} posts")
    print(f"📁 Datos guardados en: /app/posts_data.json")
    
    return len(all_posts)

if __name__ == "__main__":
    try:
        count = sync_posts()
        print(f"🎉 ¡Sincronización completada exitosamente!")
        print(f"📊 Total de posts sincronizados: {count}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
