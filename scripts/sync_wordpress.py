import requests
import os
import json
from dotenv import load_dotenv

load_dotenv('/root/content-ai/.env')

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
            print(f"❌ Error: {response.status_code}")
            break
            
        posts = response.json()
        if not posts:
            break
            
        all_posts.extend(posts)
        print(f"📥 Página {page}: {len(posts)} posts")
        page += 1
    
    # Guardar en archivo JSON para el dashboard
    posts_data = []
    for post in all_posts:
        posts_data.append({
            "id": post["id"],
            "title": post["title"]["rendered"],
            "url": post["link"],
            "date": post["date"],
            "excerpt": post["excerpt"]["rendered"] if post["excerpt"] else ""
        })
    
    # Guardar en archivo
    with open('/root/content-ai/dashboard/posts_data.json', 'w') as f:
        json.dump(posts_data, f, indent=2)
    
    print(f"✅ Sincronizados {len(all_posts)} posts")
    print(f"📁 Datos guardados en: /root/content-ai/dashboard/posts_data.json")
    
    return len(all_posts)

if __name__ == "__main__":
    sync_posts()
