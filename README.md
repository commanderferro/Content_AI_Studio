# Content AI Studio · Editorial Trends & WordPress

Content AI Studio es una herramienta que conecta un blog en WordPress con fuentes de tendencias (Google Trends, X/Twitter, etc.) para proponer temas de contenido alineados con las categorías reales del sitio, detectar contenidos demasiado parecidos a los ya publicados, sugerir nuevos enfoques y oportunidades de linkbuilding interno, y ayudar a planificar el calendario editorial.[web:44][web:52]

Incluye:
- API en FastAPI para análisis de tendencias, detección de similitud de contenidos y recomendaciones de temas.
- Dashboard en Streamlit con diseño oscuro y alto contraste.
- Integración con WordPress (REST API) para leer categorías y posts publicados.
- Base para conectar con Airtable / Supabase como calendario editorial y generación futura de borradores.

## Características

- Lee las **categorías reales** del blog vía WordPress REST API (no son categorías inventadas, sino las del sitio en producción).[web:39]
- Recupera posts publicados para analizarlos y evitar publicar artículos demasiado similares.
- Analiza posibles nuevos temas y:
  - Detecta si son **muy parecidos** a artículos ya existentes.
  - Propone cambiar el **enfoque** (por ejemplo, actualizar datos, enfoque local, convertirlo en serie/saga).
- Sugiere oportunidades de **linkbuilding interno** (posts relacionados, anchors recomendados, prioridad sugerida).
- Consulta tendencias externas (Google Trends y X/Twitter, ampliable a otras fuentes) y las cruza con las categorías del blog para generar ideas de contenido basadas en **trending topics**.[web:33][web:34]
- Genera **recomendaciones de contenido** priorizadas (ej. para hoy, mañana y pasado) que pueden usarse como base para un calendario editorial.
- Dashboard visual en Streamlit para explorar categorías, tendencias, análisis y recomendaciones.

## Arquitectura

- **Backend**: FastAPI (`backend/main.py`)
  - `TrendingTopicsAnalyzer`: lógica de:
    - Extracción de categorías del blog y sus descripciones.
    - Lectura de posts existentes.
    - Consulta de tendencias y filtrado por categorías.
    - Generación de recomendaciones de contenido.
  - Endpoints principales:
    - `GET /`  
      Estado general de la API y resumen de categorías cargadas.
    - `GET /health`  
      Estado de salud de la API (versión, número de categorías cargadas).
    - `GET /api/your-categories`  
      Devuelve las categorías reales del WordPress, cobertura estimada y resumen (categorías más y menos cubiertas).
    - `GET /api/test-wordpress`  
      Test de conexión con WordPress (usuario + Application Password) y muestra algunos posts de ejemplo.[web:39]
    - `GET /api/trending-topics`  
      Devuelve temas trending filtrados por las categorías del blog y estadísticas básicas.
    - `POST /api/content-recommendations`  
      Genera recomendaciones de contenido basadas en tendencias, categorías y posts existentes (incluyendo detección de similitud y propuestas de enfoque alternativo).
    - `GET /api/quick-recommendations`  
      Devuelve 3 recomendaciones rápidas pensadas para hoy, mañana y pasado mañana.

- **Dashboard**: Streamlit (`dashboard/app.py`)
  - UI en modo oscuro con estilos personalizados (CSS) y tarjetas de métricas.
  - Secciones para:
    - Ver estado de la API y del sistema.
    - Consultar categorías del blog y su cobertura.
    - Explorar tendencias actuales vinculadas a las categorías.
    - Ver recomendaciones de contenido, ideas rápidas y posibles sagas.
    - Base para integrar vistas de calendario editorial (por ejemplo, conectando con Airtable/Supabase).

<img width="1326" height="779" alt="dashboard" src="https://github.com/user-attachments/assets/5d4ccaee-6d2b-477f-a9ac-c21eee71b902" />

- **Integraciones**:
  - WordPress REST API (categorías y posts).
  - Fuentes de tendencias:
    - Google Trends (España y global).[web:33]
    - X/Twitter (trending por región, por ejemplo España).[web:34]
    - Ampliable a Reddit, TikTok, Instagram, LinkedIn.
  - (Opcional) Airtable / Supabase para almacenamiento «serio» del calendario editorial y logs.

## Requisitos

- Python 3.11+
- FastAPI
- Uvicorn
- Streamlit
- Requests
- python-dotenv
- (Opcional) Plotly para gráficos en el dashboard

Las dependencias principales del backend están definidas en `backend/requirements.txt`.

## Configuración

Las credenciales y URLs se gestionan mediante variables de entorno (`.env`), por ejemplo:

```env
WORDPRESS_URL=https://tu-blog.com
WORDPRESS_USER=tu_usuario
WORDPRESS_APP_PASSWORD=tu_app_password

# Ejemplos para tendencias:
TWITTER_BEARER_TOKEN=xxxx
# Otros tokens/API keys según las fuentes que añadas
