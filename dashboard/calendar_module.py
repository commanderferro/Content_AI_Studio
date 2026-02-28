"""
Módulo de Calendario Editorial (versión simplificada)
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json

def show_calendar_editorial():
    """Muestra la interfaz completa del calendario editorial"""
    
    # Título y descripción
    st.header("📅 Calendario Editorial Inteligente")
    st.markdown("""
    Genera calendarios automáticos basados en **tus categorías reales de WordPress** y **análisis de tendencias**.
    """)
    
    # Configuración
    API_BASE_URL = "http://backend:8000"
    
    # Sidebar interno para configuración
    with st.sidebar:
        st.subheader("⚙️ Configuración del Calendario")
        
        posts_per_week = st.slider(
            "Publicaciones por semana",
            1, 5, 2,
            help="¿Cuántos posts quieres publicar por semana?"
        )
        
        months_to_plan = st.slider(
            "Meses a planificar", 
            1, 6, 2,
            help="¿Cuántos meses quieres planificar?"
        )
        
        if st.button("🔄 Actualizar desde WordPress", type="secondary"):
            with st.spinner("Actualizando..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/api/your-categories")
                    if response.status_code == 200:
                        st.success("✅ Categorías actualizadas")
                    else:
                        st.error("❌ Error actualizando")
                except:
                    st.error("⚠️ No se pudo conectar al backend")
    
    # Pestañas del calendario
    cal_tab1, cal_tab2 = st.tabs(["📋 Generar Calendario", "📊 Tus Categorías"])
    
    with cal_tab1:
        show_calendar_generator(API_BASE_URL, posts_per_week, months_to_plan)
    
    with cal_tab2:
        show_categories_analysis(API_BASE_URL)

def show_calendar_generator(api_url, posts_per_week, months):
    """Muestra el generador de calendario"""
    
    st.subheader("Generar Nuevo Calendario")
    
    if st.button("🎯 Generar Calendario Inteligente", type="primary", use_container_width=True):
        with st.spinner("Analizando categorías y generando calendario..."):
            try:
                # Obtener datos de categorías
                response = requests.get(f"{api_url}/api/your-categories", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        # Generar calendario
                        calendar = generate_calendar_from_data(
                            data, 
                            posts_per_week, 
                            months
                        )
                        
                        # Mostrar resultados
                        display_calendar_results(calendar)
                        
                        # Mostrar estadísticas
                        display_calendar_stats(calendar)
                        
                        # Opciones de exportación
                        display_export_options(calendar)
                        
                    else:
                        st.error("No se pudieron obtener los datos de categorías")
                else:
                    st.error(f"Error del servidor: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Vista rápida
    with st.expander("👁️ Vista Previa Rápida", expanded=False):
        st.write("Ejemplo de cómo quedaría tu calendario:")
        
        preview_data = [
            {"Fecha": (datetime.now() + timedelta(days=i*3)).strftime("%Y-%m-%d"),
             "Día": (datetime.now() + timedelta(days=i*3)).strftime("%A")[:3],
             "Categoría": ["IA", "Programación", "Tecnología", "LLM"][i % 4],
             "Tema": f"Guía de {['IA', 'programación', 'tecnología', 'LLM'][i % 4]}",
             "Estado": "📝 Planificado"}
            for i in range(5)
        ]
        
        st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)

def show_categories_analysis(api_url):
    """Muestra análisis de categorías"""
    
    st.subheader("📊 Análisis de Tus Categorías")
    
    try:
        response = requests.get(f"{api_url}/api/your-categories", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                categories = data.get("categories", [])
                coverage = data.get("coverage", {})
                
                # Mostrar estadísticas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total categorías", len(categories))
                with col2:
                    total_posts = sum(coverage.values())
                    st.metric("Posts estimados", total_posts)
                with col3:
                    avg_posts = total_posts / len(categories) if categories else 0
                    st.metric("Media por categoría", f"{avg_posts:.1f}")
                
                # Mostrar categorías con conteo
                st.subheader("📋 Lista de Categorías")
                
                for i, cat in enumerate(categories[:20]):
                    posts_count = coverage.get(cat, 0)
                    
                    col_cat1, col_cat2 = st.columns([3, 1])
                    with col_cat1:
                        st.write(f"**{i+1}. {cat.title()}**")
                    with col_cat2:
                        st.metric("Posts", posts_count, label_visibility="collapsed")
                
                # Mostrar tabla completa
                st.subheader("📈 Tabla Completa de Categorías")
                df_cats = pd.DataFrame([
                    {"Categoría": cat, "Posts": coverage.get(cat, 0)}
                    for cat in categories
                ])
                st.dataframe(df_cats.sort_values("Posts", ascending=False), use_container_width=True)
            
            else:
                st.info("No se pudieron cargar las categorías")
        else:
            st.error(f"Error del servidor: {response.status_code}")
            
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")

def generate_calendar_from_data(categories_data, posts_per_week, months):
    """Genera un calendario a partir de los datos de categorías"""
    
    calendar = []
    
    # Obtener categorías
    categories = categories_data.get("categories", ["IA", "Tecnología", "Programación"])
    coverage = categories_data.get("coverage", {})
    
    # Determinar días de publicación
    if posts_per_week == 1:
        pub_days = [0]  # Lunes
    elif posts_per_week == 2:
        pub_days = [0, 3]  # Lunes y Jueves
    elif posts_per_week == 3:
        pub_days = [0, 2, 4]  # Lunes, Miércoles, Viernes
    else:
        pub_days = [0, 1, 3, 4]  # Lunes, Martes, Jueves, Viernes
    
    # Generar fechas
    start_date = datetime.now()
    publications_needed = posts_per_week * 4 * months  # Aprox 4 semanas por mes
    
    for i in range(publications_needed * 7):  # Buscar suficientes días
        current_date = start_date + timedelta(days=i)
        
        if current_date.weekday() in pub_days and len(calendar) < publications_needed:
            # Seleccionar categoría (rotación balanceada)
            cat_idx = len(calendar) % len(categories)
            category = categories[cat_idx]
            
            # Generar tema
            topic = generate_topic_for_category(category, current_date, coverage.get(category, 0))
            
            # Determinar tipo de contenido
            content_type = determine_content_type(coverage.get(category, 0))
            
            calendar.append({
                "Fecha": current_date.strftime("%Y-%m-%d"),
                "Día": current_date.strftime("%A")[:3],
                "Categoría": category.title(),
                "Tema": topic,
                "Tipo": content_type,
                "Palabras estimadas": estimate_word_count(content_type),
                "Prioridad": "Alta" if len(calendar) == 0 else "Media",
                "Keywords": generate_keywords(category)
            })
    
    return calendar

def generate_topic_for_category(category, date, post_count):
    """Genera un tema para una categoría específica"""
    
    month = date.strftime("%B")
    
    # Títulos basados en cantidad de posts existentes
    if post_count == 0:
        templates = [
            f"Guía completa de {category} para principiantes",
            f"Todo lo que necesitas saber sobre {category}",
            f"{category.title()}: introducción completa"
        ]
    elif post_count == 1:
        templates = [
            f"Profundizando en {category}: conceptos avanzados",
            f"{category.title()} en la práctica: casos reales",
            f"Optimización y mejores prácticas en {category}"
        ]
    else:
        templates = [
            f"Actualización {month}: novedades en {category}",
            f"{category.title()} en 2024: tendencias y predicciones",
            f"Comparativa de herramientas para {category}",
            f"Caso de estudio: implementación exitosa de {category}"
        ]
    
    import random
    return random.choice(templates)

def determine_content_type(post_count):
    """Determina el tipo de contenido basado en posts existentes"""
    if post_count == 0:
        return "Guía completa"
    elif post_count <= 2:
        return "Tutorial práctico"
    else:
        return "Análisis/Actualización"

def estimate_word_count(content_type):
    """Estima palabras según tipo de contenido"""
    if content_type == "Guía completa":
        return 1800
    elif content_type == "Tutorial práctico":
        return 1200
    else:
        return 1000

def generate_keywords(category):
    """Genera keywords para una categoría"""
    keywords_map = {
        "ia": "IA, inteligencia artificial, machine learning",
        "tecnología": "tecnología, innovación, gadgets",
        "programación": "programación, código, desarrollo",
        "llm": "LLM, modelos de lenguaje, GPT",
        "prompts": "prompts, prompt engineering",
        "cibeseguridad": "ciberseguridad, seguridad, hacking"
    }
    
    for key, keywords in keywords_map.items():
        if key in category.lower():
            return keywords
    
    return f"{category}, guía, tutorial"

def display_calendar_results(calendar):
    """Muestra el calendario generado"""
    
    st.subheader("🗓️ Calendario Generado")
    
    df = pd.DataFrame(calendar)
    st.dataframe(
        df[["Fecha", "Día", "Categoría", "Tema", "Tipo", "Prioridad"]],
        use_container_width=True,
        hide_index=True
    )

def display_calendar_stats(calendar):
    """Muestra estadísticas del calendario"""
    
    df = pd.DataFrame(calendar)
    
    st.subheader("📊 Estadísticas del Calendario")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total publicaciones", len(calendar))
    
    with col2:
        categories = df["Categoría"].nunique()
        st.metric("Categorías cubiertas", categories)
    
    with col3:
        if "Palabras estimadas" in df.columns:
            avg_words = df["Palabras estimadas"].mean()
            st.metric("Palabras promedio", f"{int(avg_words)}")
        else:
            st.metric("Tipo predominante", df["Tipo"].mode()[0] if not df.empty else "N/A")
    
    with col4:
        high_priority = len(df[df["Prioridad"] == "Alta"])
        st.metric("Prioridad alta", high_priority)

def display_export_options(calendar):
    """Muestra opciones para exportar el calendario"""
    
    st.subheader("📤 Exportar Calendario")
    
    df = pd.DataFrame(calendar)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Exportar a CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📊 CSV (Excel)",
            data=csv,
            file_name=f"calendario_editorial_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Exportar a JSON
        json_data = json.dumps(calendar, indent=2, ensure_ascii=False)
        st.download_button(
            label="📝 JSON (API)",
            data=json_data,
            file_name=f"calendario_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Exportar a Markdown
        md_lines = ["# Calendario Editorial", "", f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
        for entry in calendar:
            md_lines.append(f"## {entry['Fecha']} ({entry['Día']})")
            md_lines.append(f"- **Categoría**: {entry['Categoría']}")
            md_lines.append(f"- **Tema**: {entry['Tema']}")
            md_lines.append(f"- **Tipo**: {entry['Tipo']}")
            md_lines.append(f"- **Prioridad**: {entry['Prioridad']}")
            md_lines.append("")
        
        md_content = "\n".join(md_lines)
        st.download_button(
            label="📖 Markdown",
            data=md_content,
            file_name=f"calendario_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )
