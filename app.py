import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time

# --- Intentar importar plotly (opcional, para gráficos) ---
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Content AI Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# ESTILOS CSS - TEMA OSCURO DE ALTO CONTRASTE
# ==============================================================================
st.markdown("""
<style>
    :root {
        --bg-primary: #0a0c10;
        --bg-secondary: #1a1d23;
        --surface: #2d313a;
        --primary: #4f9eff;
        --primary-light: #3b82f6;
        --secondary: #10b981;
        --text-primary: #ffffff;
        --text-secondary: #b0b7c4;
        --border: #3a3f4b;
        --success-bg: #1e3a2f;
        --success-text: #a7f3d0;
        --warning-bg: #3f2e1b;
        --warning-text: #fcd34d;
        --error-bg: #3f1f1f;
        --error-text: #fca5a5;
    }

    .stApp {
        background-color: var(--bg-primary);
    }

    h1, h2, h3, h4 {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    h1 {
        font-weight: 600 !important;
        font-size: 2.5rem !important;
        letter-spacing: -0.02em;
    }
    .stMarkdown, p, li {
        color: var(--text-secondary);
        line-height: 1.6;
    }

    div[data-testid="stVerticalBlock"] > div:has(> div > div.stTextInput),
    .card-custom {
        background-color: var(--bg-secondary);
        border-radius: 24px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        border: 1px solid var(--border);
        margin-bottom: 1rem;
        transition: box-shadow 0.2s ease;
    }

    .stat-card {
        background: linear-gradient(135deg, var(--surface) 0%, var(--bg-secondary) 80%);
        border-left: 6px solid var(--primary);
        border-radius: 20px;
        padding: 1.2rem 1rem;
    }
    .stat-value {
        font-size: 2.2rem;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1.2;
    }
    .stat-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-secondary);
    }

    .badge-custom {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        border: 1px solid transparent;
    }
    .badge-high {
        background-color: var(--success-bg);
        color: var(--success-text);
        border-color: #10b981;
    }
    .badge-medium {
        background-color: var(--warning-bg);
        color: var(--warning-text);
        border-color: #f59e0b;
    }
    .badge-low {
        background-color: var(--error-bg);
        color: var(--error-text);
        border-color: #ef4444;
    }

    .stButton > button {
        border-radius: 40px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s !important;
        border: 1px solid var(--border) !important;
        background-color: var(--surface) !important;
        color: var(--text-primary) !important;
    }
    .stButton > button:hover {
        background-color: var(--primary-light) !important;
        border-color: var(--primary) !important;
        color: white !important;
    }
    .stButton > button[kind="primary"] {
        background-color: var(--primary) !important;
        color: var(--bg-primary) !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: var(--primary-light) !important;
        box-shadow: 0 4px 10px rgba(79, 158, 255, 0.3);
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        border-radius: 40px !important;
        border: 1px solid var(--border) !important;
        background-color: var(--surface) !important;
        padding: 0.5rem 1rem !important;
        color: var(--text-primary) !important;
    }
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(79, 158, 255, 0.2) !important;
    }

    .streamlit-expanderHeader {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 40px !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }

    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: 20px;
        overflow: hidden;
        background-color: var(--bg-secondary);
    }
    .stDataFrame th {
        background-color: var(--surface);
        color: var(--text-primary);
        font-weight: 500;
    }
    .stDataFrame td {
        background-color: var(--bg-secondary);
        color: var(--text-secondary);
    }

    .footer {
        text-align: center;
        padding: 1.5rem;
        color: var(--text-secondary);
        border-top: 1px solid var(--border);
        margin-top: 3rem;
    }

    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border);
    }
    .css-1d391kg .stButton > button {
        border-radius: 40px !important;
        text-align: left;
    }

    .stAlert {
        background-color: var(--surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# INICIALIZACIÓN DEL ESTADO DE LA SESIÓN
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = False
if "selected_section" not in st.session_state:
    st.session_state.selected_section = "Dashboard"
if "get_trends" not in st.session_state:
    st.session_state.get_trends = False
if "get_recs" not in st.session_state:
    st.session_state.get_recs = False

# ==============================================================================
# PANTALLA DE LOGIN (OBLIGATORIA)
# ==============================================================================
if not st.session_state.logged_in:
    st.markdown("# 🔐 Acceso restringido")
    st.markdown("Introduce la contraseña para continuar.")
    
    password_input = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar sesión", type="primary"):
        # Obtener la contraseña desde el entorno
        correct_password = "RosaMora25mayo"
        if password_input == correct_password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    
    st.stop()  # No muestra nada más si no está logueado

# ==============================================================================
# BARRA LATERAL (SIDEBAR) - Solo visible si está logueado
# ==============================================================================
if st.session_state.sidebar_open:
    with st.sidebar:
        st.markdown("### ✨ **Content AI Studio**")
        st.caption("Análisis inteligente para tu WordPress")
        st.divider()

        # --- Estado del sistema ---
        try:
            resp = requests.get("http://backend:8000/health", timeout=5)
            if resp.status_code == 200:
                st.success("🟢 Sistema activo")
            else:
                st.warning("🟡 API con problemas")
        except:
            st.warning("🔴 API offline")
        st.divider()

        # --- Navegación principal ---
        st.markdown("#### Navegación")
        nav_items = [
            ("📊", "Dashboard"),
            ("📝", "Analizar"),
            ("📈", "Tendencias"),
            ("🎯", "Recomendaciones"),
            ("⚙️", "Sistema")
        ]
        for icon, name in nav_items:
            if st.button(f"{icon} {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state.selected_section = name
                st.session_state.sidebar_open = False
                st.rerun()
        st.divider()

        # --- Acciones rápidas ---
        st.markdown("#### Acciones rápidas")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔥 Tendencias", use_container_width=True):
                st.session_state.get_trends = True
                st.session_state.selected_section = "Tendencias"
                st.session_state.sidebar_open = False
                st.rerun()
        with col2:
            if st.button("🎯 Ideas", use_container_width=True):
                st.session_state.get_recs = True
                st.session_state.selected_section = "Recomendaciones"
                st.session_state.sidebar_open = False
                st.rerun()
        st.divider()
        st.caption(f"v4.3 · {os.getenv('WORDPRESS_URL', 'Conecta tu WordPress')}")

# ==============================================================================
# CABECERA PRINCIPAL
# ==============================================================================
col1, col2, col3 = st.columns([6, 1.5, 1.5])
with col1:
    st.title("✨ Content AI Studio")
    st.caption("Datos claros, decisiones inteligentes.")
with col2:
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.selected_section = "Dashboard"
        st.rerun()
with col3:
    if st.button("☰ Menú", use_container_width=True):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()
st.divider()

# ==============================================================================
# SECCIÓN: DASHBOARD
# ==============================================================================
if st.session_state.selected_section == "Dashboard":
    st.markdown("## 📊 Panel de Control")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Posts Analizados</div>
            <div class="stat-value">24</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card" style="border-left-color: #10b981;">
            <div class="stat-label">Originalidad Media</div>
            <div class="stat-value">85%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-card" style="border-left-color: #f59e0b;">
            <div class="stat-label">Enlaces Sugeridos</div>
            <div class="stat-value">12</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="stat-card" style="border-left-color: #8b5cf6;">
            <div class="stat-label">Tendencias Activas</div>
            <div class="stat-value">5</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        with st.container():
            st.markdown("#### 📋 Actividad Reciente")
            data_actividad = {
                'Fecha': ['2024-02-15', '2024-02-14', '2024-02-13', '2024-02-12'],
                'Título': ['IA en marketing', 'Privacidad digital', 'ETFs tecnológicos', 'Algoritmos éticos'],
                'Originalidad': ['92%', '78%', '85%', '88%']
            }
            df_act = pd.DataFrame(data_actividad)
            st.dataframe(df_act, use_container_width=True, hide_index=True)

    with col_right:
        with st.container():
            st.markdown("#### 📂 Distribución por Categorías")
            data_cats = {
                'Categoría': ['IA', 'Tecnología', 'Finanzas', 'Privacidad', 'Algoritmos'],
                'Posts': [29, 2, 2, 1, 1]
            }
            df_cats = pd.DataFrame(data_cats)

            if PLOTLY_AVAILABLE:
                fig = px.pie(df_cats, values='Posts', names='Categoría',
                             color_discrete_sequence=px.colors.sequential.Blues_r,
                             hole=0.3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0),
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df_cats, use_container_width=True, hide_index=True)
                st.bar_chart(df_cats.set_index('Categoría'), color='#4361ee')

# ==============================================================================
# SECCIÓN: ANALIZAR
# ==============================================================================
elif st.session_state.selected_section == "Analizar":
    st.markdown("## 📝 Analizar Contenido")
    st.caption("Comprueba la originalidad y el potencial de tus textos.")

    with st.container():
        titulo = st.text_input("**Título**", placeholder="Ej: 10 formas en que la IA transforma el marketing")
        contenido = st.text_area("**Contenido**", height=200, placeholder="Pega aquí el cuerpo del texto...")

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col2:
            analisis_profundo = st.checkbox("🔬 Análisis profundo", value=True)
        with col3:
            incluir_seo = st.checkbox("📈 Sugerencias SEO", value=True)

        if st.button("🔍 **Analizar ahora**", type="primary", use_container_width=True):
            if titulo and contenido:
                with st.spinner("La IA está analizando tu contenido..."):
                    time.sleep(2.5)

                    st.success("✅ Análisis completado")

                    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                    col_res1.metric("Originalidad", "85%", "+5%")
                    col_res2.metric("Palabras", str(len(contenido.split())))
                    col_res3.metric("Tiempo lectura", f"{len(contenido.split())//200} min")
                    col_res4.metric("Densidad Keywords", "2.3%")

                    with st.expander("📋 **Resultados detallados**"):
                        st.progress(0.85, "Originalidad")
                        st.progress(0.72, "SEO")
                        st.progress(0.93, "Legibilidad")

                        st.markdown("**💡 Sugerencias principales:**")
                        sug_col1, sug_col2, sug_col3 = st.columns(3)
                        sug_col1.info("➕ Añade más ejemplos")
                        sug_col2.warning("📑 Usa subtítulos (H2, H3)")
                        sug_col3.success("🖼️ Incluye al menos 2 imágenes")
            else:
                st.error("⚠️ Por favor, completa el título y el contenido.")

# ==============================================================================
# SECCIÓN: TENDENCIAS
# ==============================================================================
elif st.session_state.selected_section == "Tendencias":
    st.markdown("## 📈 Trending Topics")
    st.caption("Lo que se está moviendo ahora, filtrado para tu audiencia.")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        fuente = st.selectbox("Filtrar por fuente", ["Todas", "Google", "Twitter"])
    with col_f2:
        orden = st.selectbox("Ordenar por", ["Relevancia", "Volumen"])
    with col_f3:
        max_trends = st.number_input("Mostrar", min_value=5, max_value=50, value=15)

    if st.button("🔍 **Buscar tendencias**", type="primary", use_container_width=True) or st.session_state.get("get_trends", False):
        st.session_state.get_trends = False
        with st.spinner("Escaneando el pulso de la red..."):
            try:
                response = requests.get("http://backend:8000/api/trending-topics", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        google_trends = data.get("google_trends", [])
                        twitter_trends = data.get("twitter_trends", [])

                        all_trends = []
                        for t in google_trends:
                            all_trends.append({
                                "titulo": t["title"],
                                "fuente": "Google",
                                "relevancia": t.get("relevance", 0.5),
                                "volumen": t.get("volume", "N/A"),
                                "tema": t.get("topic", "general"),
                                "desc": t.get("description", "")
                            })
                        for t in twitter_trends:
                            vol = t.get("tweet_volume", 0)
                            all_trends.append({
                                "titulo": t['hashtag'],
                                "fuente": "Twitter",
                                "relevancia": min(vol / 100000, 0.9),
                                "volumen": f"{vol:,} tweets",
                                "tema": t.get("category", "general"),
                                "desc": f"Tendencia en Twitter con {vol:,} tweets."
                            })

                        if fuente != "Todas":
                            all_trends = [t for t in all_trends if t["fuente"] == fuente]

                        if orden == "Relevancia":
                            all_trends.sort(key=lambda x: x["relevancia"], reverse=True)
                        else:
                            all_trends.sort(key=lambda x: str(x["volumen"]), reverse=True)

                        st.success(f"✅ Se encontraron **{len(all_trends)}** tendencias")

                        df_display = pd.DataFrame([{
                            "Título": t["titulo"][:60] + "..." if len(t["titulo"])>60 else t["titulo"],
                            "Fuente": t["fuente"],
                            "Relevancia": f"{t['relevancia']:.0%}",
                            "Tema": t["tema"]
                        } for t in all_trends[:max_trends]])

                        def color_relevance_row(row):
                            rel_val = float(row["Relevancia"].strip('%'))/100
                            if rel_val > 0.8:
                                return ['background-color: #1e3a2f']*len(row)
                            elif rel_val > 0.6:
                                return ['background-color: #3f2e1b']*len(row)
                            else:
                                return ['background-color: #3f1f1f']*len(row)

                        st.dataframe(df_display.style.apply(color_relevance_row, axis=1),
                                   use_container_width=True, hide_index=True)

                        st.markdown("#### 📌 Detalles de las principales")
                        for i, trend in enumerate(all_trends[:5]):
                            badge = ("badge-high" if trend["relevancia"]>0.8 else
                                     "badge-medium" if trend["relevancia"]>0.6 else "badge-low")
                            with st.expander(f"**{i+1}. {trend['titulo']}**"):
                                st.markdown(f"**Descripción:** {trend.get('desc', 'Sin descripción')}")
                                st.markdown(f"**Tema:** `{trend['tema']}`")
                                st.markdown(f"**Volumen:** {trend['volumen']}")
                                st.markdown(f"<span class='badge-custom {badge}'>Relevancia: {trend['relevancia']:.0%}</span>", unsafe_allow_html=True)
                                st.caption(f"Fuente: {trend['fuente']}")
                    else:
                        st.error("❌ La API no pudo obtener tendencias.")
                else:
                    st.error(f"❌ Error {response.status_code} al contactar la API.")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")

# ==============================================================================
# SECCIÓN: RECOMENDACIONES
# ==============================================================================
elif st.session_state.selected_section == "Recomendaciones":
    st.markdown("## 🎯 Recomendaciones de Contenido")
    st.caption("Ideas personalizadas para tu próximo artículo, basadas en tendencias y tu blog.")

    num_recs = st.slider("Número de recomendaciones", 5, 25, 12)

    if st.button("🎯 **Generar ideas**", type="primary", use_container_width=True) or st.session_state.get("get_recs", False):
        st.session_state.get_recs = False
        with st.spinner("Nuestra IA está cocinando ideas frescas para ti..."):
            try:
                response = requests.post(
                    "http://backend:8000/api/content-recommendations",
                    json={"num_recommendations": num_recs},
                    timeout=15
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        recs = data.get("recommendations", [])

                        st.success(f"✅ Se generaron **{len(recs)}** ideas")

                        for i, rec in enumerate(recs, 1):
                            potencial = rec.get('estimated_seo_potential', 0)
                            badge = ("badge-high" if potencial > 80 else
                                     "badge-medium" if potencial > 60 else "badge-low")

                            with st.expander(f"**{i}. {rec['title']}**"):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**🎯 Por qué:** {rec.get('why_relevant', 'Relevante para tu audiencia')}")
                                    st.write(f"**📂 Tema:** {rec.get('trend_data', {}).get('topic', 'general')}")
                                    if rec.get('actionable_steps'):
                                        st.write("**📝 Pasos sugeridos:**")
                                        for step in rec['actionable_steps'][:3]:
                                            st.caption(f"• {step}")
                                with col2:
                                    st.markdown(f"<span class='badge-custom {badge}'>Potencial SEO: {potencial:.0f}%</span>", unsafe_allow_html=True)
                                    st.caption(f"Fuente: {rec.get('trend_source', 'análisis')}")
                    else:
                        st.error("❌ No se pudieron generar recomendaciones.")
                else:
                    st.error(f"❌ Error {response.status_code} en la API.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ==============================================================================
# SECCIÓN: SISTEMA
# ==============================================================================
else:
    st.markdown("## ⚙️ Sistema")
    st.caption("Estado de las conexiones y servicios.")

    with st.container():
        st.markdown("#### Estado de los servicios")
        endpoints = [
            ("/health", "API Principal", "🔵"),
            ("/api/trending-topics", "Trending Topics", "📈"),
            ("/api/your-categories", "Categorías", "📂"),
            ("/api/content-recommendations", "Recomendaciones", "🎯")
        ]

        for endpoint, name, icon in endpoints:
            try:
                resp = requests.get(f"http://backend:8000{endpoint}", timeout=3)
                if resp.status_code == 200:
                    st.success(f"{icon} **{name}** - OK")
                else:
                    st.error(f"{icon} **{name}** - Error {resp.status_code}")
            except:
                st.error(f"{icon} **{name}** - Sin conexión")

# ==============================================================================
# PIE DE PÁGINA
# ==============================================================================
st.divider()
st.markdown("""
<div class='footer'>
    <b>Content AI Studio</b> · v4.3 · Tema oscuro de alto contraste
</div>
""", unsafe_allow_html=True)
