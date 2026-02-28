# Sidebar
with st.sidebar:
    st.header("🎯 Navegación")
    
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown("---")
    
    # Opciones de navegación (EN EL ORDEN QUE PEDISTE)
    st.subheader("📂 Secciones")
    
    # Usar radio buttons para navegación persistente
    nav_option = st.radio(
        "Ir a:",
        ["📝 Analizar Contenido", "🔗 Analizar + Enlaces", "📅 Calendario Editorial", 
         "📈 Trending Topics", "🎯 Recomendaciones", "⚙️ Sistema"],
        label_visibility="collapsed"
    )
    
    # Actualizar pestaña seleccionada cuando cambia la opción
    if nav_option != st.session_state.get('selected_tab', '📝 Analizar Contenido'):
        st.session_state.selected_tab = nav_option
        st.rerun()
    
    st.markdown("---")
    
    # Estado del sistema
    try:
        resp = requests.get("http://backend:8000/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            st.success(f"✅ v{data.get('version', '4.0')}")
        else:
            st.warning(f"⚠️ API: {resp.status_code}")
    except:
        st.warning("⚠️ API offline")
    
    st.markdown("---")
    
    # Acciones rápidas
    if st.button("🔄 Obtener Tendencias Ahora", type="primary"):
        st.session_state.get_trends = True
        st.session_state.selected_tab = "📈 Trending Topics"
        st.rerun()
    
    if st.button("🎯 Recomendaciones Rápidas"):
        st.session_state.get_quick_recs = True
        st.session_state.selected_tab = "🎯 Recomendaciones"
        st.rerun()
    
    st.markdown("---")
    st.caption("http://148.230.118.46:8501")
