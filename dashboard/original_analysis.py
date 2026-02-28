"""
Función de Análisis de Originalidad
Compara contenido nuevo con todos los artículos del blog
"""
import streamlit as st
import requests
import pandas as pd

def show_originality_analysis():
    """Analiza si el contenido es original comparando con el blog"""
    
    st.header("📝 Analizar Originalidad del Contenido")
    st.markdown("""
    **¿Qué hace este análisis?**
    - Compara tu contenido con TODOS los artículos de tu blog
    - Detecta si el tema ya está cubierto
    - Sugiere ángulos diferentes si hay similitudes
    - Evalúa la novedad del contenido
    """)
    
    # API configuration
    API_URL = "http://backend:8000"
    
    # Inputs
    col1, col2 = st.columns([3, 1])
    
    with col1:
        title = st.text_input(
            "Título del artículo",
            placeholder="Ej: Guía completa de IA generativa para negocios",
            help="Título completo del artículo que quieres analizar"
        )
    
    with col2:
        post_id = st.number_input(
            "ID WordPress (opcional)",
            min_value=0,
            value=0,
            help="Si ya existe en WordPress, pon su ID"
        )
    
    content = st.text_area(
        "Contenido completo",
        height=250,
        placeholder="Pega aquí el contenido completo del artículo...\n\nLa IA generativa está transformando cómo las empresas operan. Desde automatización de procesos hasta generación de contenido, las aplicaciones son infinitas...",
        help="Mínimo 200 palabras para un análisis preciso"
    )
    
    # Opciones de análisis
    with st.expander("⚙️ Opciones de Análisis Avanzado", expanded=False):
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            check_similarity = st.checkbox("Buscar contenido similar", True)
            check_keywords = st.checkbox("Analizar densidad de keywords", True)
        
        with col_opt2:
            min_similarity = st.slider("Umbral de similitud", 0.1, 1.0, 0.7)
            suggest_alternatives = st.checkbox("Sugerir ángulos alternativos", True)
    
    # Botón de análisis
    if st.button("🔍 Analizar Originalidad", type="primary", use_container_width=True):
        if not title or not content:
            st.warning("⚠️ Por favor, introduce título y contenido")
            return
        
        if len(content.split()) < 50:
            st.warning("⚠️ El contenido es muy corto. Para un análisis preciso, introduce al menos 200 palabras.")
        
        with st.spinner("🔍 Analizando contenido y comparando con tu blog..."):
            try:
                # Enviar para análisis (usaremos endpoint existente o similar)
                response = requests.post(
                    f"{API_URL}/api/analyze",
                    json={
                        "title": title,
                        "content": content,
                        "post_id": post_id if post_id > 0 else None
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Mostrar resultados principales
                    display_originality_results(result, title, content)
                    
                elif response.status_code == 404:
                    # Si el endpoint /api/analyze no existe, usar alternativa
                    st.info("ℹ️ Usando análisis simplificado...")
                    simplified_analysis(title, content)
                else:
                    st.error(f"❌ Error del servidor: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("🚫 No se puede conectar al servidor de análisis")
                st.info("El backend debe estar ejecutándose en http://backend:8000")
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")

def display_originality_results(result, title, content):
    """Muestra los resultados del análisis de originalidad"""
    
    # Encabezado de resultados
    st.subheader("🎯 Resultados del Análisis")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        originality_score = result.get("score", 0.8) * 100
        st.metric("Puntuación de Originalidad", f"{originality_score:.1f}%")
        
        # Barra de progreso visual
        st.progress(originality_score/100)
    
    with col2:
        is_novel = result.get("is_novel", True)
        if is_novel:
            st.success("✅ CONTENIDO ORIGINAL")
        else:
            st.warning("⚠️ CONTENIDO SIMILAR")
        
        word_count = result.get("word_count", len(content.split()))
        st.metric("Palabras", word_count)
    
    with col3:
        similar_count = len(result.get("similar_posts", []))
        st.metric("Posts similares", similar_count)
        
        if "reading_time" in result:
            st.metric("Tiempo lectura", f"{result['reading_time']} min")
    
    # Análisis detallado
    with st.expander("📊 Análisis Detallado", expanded=True):
        
        # Posts similares encontrados
        similar_posts = result.get("similar_posts", [])
        if similar_posts:
            st.write("### 📚 Contenido Similar Encontrado")
            
            for i, post in enumerate(similar_posts[:3]):
                col_post1, col_post2 = st.columns([4, 1])
                
                with col_post1:
                    st.write(f"**{i+1}. {post.get('title', 'Post sin título')}**")
                    if post.get('similarity_reason'):
                        st.write(f"*{post['similarity_reason']}*")
                
                with col_post2:
                    similarity = post.get('similarity', 0) * 100
                    st.metric("Similitud", f"{similarity:.0f}%")
            
            if len(similar_posts) > 3:
                st.write(f"... y {len(similar_posts) - 3} posts más")
        
        # Análisis de contenido
        analysis = result.get("analysis", {})
        if analysis:
            st.write("### 🔍 Análisis del Contenido")
            
            for key, value in analysis.items():
                if key == "keyword_density":
                    st.write("**Densidad de keywords:**")
                    for kw, density in value.items():
                        st.write(f"- {kw}: {density:.2f}%")
                elif key == "content_structure":
                    st.write(f"**Estructura:** {value}")
                else:
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Sugerencias
        suggestions = result.get("suggestions", [])
        if suggestions:
            st.write("### 💡 Sugerencias de Mejora")
            for suggestion in suggestions:
                st.write(f"- {suggestion}")
    
    # Recomendaciones finales
    st.subheader("🎯 Recomendación Final")
    
    is_novel = result.get("is_novel", True)
    originality_score = result.get("score", 0.8)
    
    if originality_score > 0.8:
        st.success("""
        **✅ EXCELENTE - Contenido altamente original**
        
        **Acciones recomendadas:**
        1. **Publicar inmediatamente** - El contenido es fresco y único
        2. **Optimizar para SEO** - Añadir meta descripción y keywords
        3. **Promover en redes** - Compartir en tus canales
        4. **Considerar serie** - Podrías expandir el tema en varios posts
        """)
    elif originality_score > 0.6:
        st.info("""
        **👍 BUENO - Contenido con ángulo único**
        
        **Acciones recomendadas:**
        1. **Publicar con ajustes** - Añadir perspectiva personal
        2. **Enlazar a posts similares** - Crear red interna
        3. **Profundizar en aspectos únicos** - Resaltar lo diferente
        4. **Actualizar posts antiguos** - Si hay similitudes, mejóralos
        """)
    else:
        st.warning("""
        **⚠️ ATENCIÓN - Contenido muy similar a existente**
        
        **Considera:**
        1. **Buscar ángulo diferente** - ¿Qué puedes aportar nuevo?
        2. **Actualizar post existente** - Mejorar contenido viejo
        3. **Fusionar contenidos** - Crear mega-guía completa
        4. **Cambiar enfoque** - Dirigir a audiencia diferente
        
        **Preguntas para nuevo ángulo:**
        - ¿Qué ha cambiado desde que escribiste posts similares?
        - ¿Hay nuevas herramientas/tendencias?
        - ¿Puedes hacerlo más práctico/con ejemplos?
        """)
    
    # Estadísticas adicionales
    with st.expander("📈 Estadísticas Adicionales", expanded=False):
        # Calcular párrafos correctamente (sin backslash en f-string)
        newline_count = content.count('\n')
        paragraph_count = content.count('\n\n') + 1 if newline_count > 0 else 1
        
        stats_data = {
            "Métrica": ["Longitud del título", "Densidad de párrafos", "Promedio oraciones/párrafo", 
                       "Palabras por oración", "Uso de subtítulos", "Enlaces sugeridos"],
            "Valor": [
                f"{len(title)} caracteres",
                f"{paragraph_count} párrafos",
                f"{(content.count('.') + content.count('!') + content.count('?')) / max(1, paragraph_count):.1f}",
                f"{len(content.split()) / max(1, content.count('.') + content.count('!') + content.count('?')):.1f}",
                "✅ Adecuado" if content.count('##') > 2 else "⚠️ Mejorable",
                f"{len(result.get('internal_links', []))} enlaces"
            ]
        }
        
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

def simplified_analysis(title, content):
    """Análisis simplificado si el backend no está disponible"""
    
    st.info("🔧 Usando análisis local simplificado")
    
    # Análisis básico
    word_count = len(content.split())
    title_length = len(title)
    paragraph_count = content.count('\n\n') + 1 if content.count('\n') > 0 else 1
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Palabras", word_count)
    
    with col2:
        st.metric("Longitud título", f"{title_length} chars")
    
    with col3:
        st.metric("Párrafos", paragraph_count)
    
    # Evaluación simple
    if word_count < 300:
        st.warning("⚠️ Contenido muy corto para análisis preciso")
        originality_score = 0.7
    elif word_count > 800:
        st.success("✅ Contenido de buena longitud")
        originality_score = 0.85
    else:
        originality_score = 0.75
    
    # Mostrar resultados
    st.subheader("📊 Evaluación de Originalidad")
    st.progress(originality_score)
    st.metric("Puntuación estimada", f"{originality_score * 100:.0f}%")
    
    # Sugerencias generales
    st.subheader("💡 Sugerencias Generales")
    
    suggestions = [
        "Asegúrate de incluir datos específicos y ejemplos",
        "Añade subtítulos H2 y H3 para mejorar estructura",
        "Incluye al menos 2-3 imágenes relevantes",
        "Optimiza el título para incluir keywords principales",
        "Considera añadir sección de preguntas frecuentes"
    ]
    
    for suggestion in suggestions:
        st.write(f"- {suggestion}")
    
    st.info("""
    **Nota:** Este es un análisis simplificado. Para análisis completo, 
    asegúrate que el backend esté ejecutándose en http://backend:8000
    """)
