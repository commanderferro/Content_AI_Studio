# Sidebar
with st.sidebar:
    st.header("🎯 Navegación")
    
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown("---")
    
    # Opciones de navegación con selectbox (más fiable)
    st.subheader("📂 Navegar a:")
    
    # Selectbox para navegación
    selected_section = st.selectbox(
        "Selecciona sección:",
        ["📝 Analizar Contenido", "🔗 Analizar + Enlaces", "📅 Calendario Editorial", 
         "📈 Trending Topics", "🎯 Recomendaciones", "⚙️ Sistema"],
        index=["📝 Analizar Contenido", "🔗 Analizar + Enlaces", "📅 Calendario Editorial", 
               "📈 Trending Topics", "🎯 Recomendaciones", "⚙️ Sistema"].index(
                   st.session_state.get('selected_tab', '📝 Analizar Contenido')),
        label_visibility="collapsed"
    )
    
    # Botón para aplicar navegación
    if st.button("🚀 Ir a la sección", type="primary", use_container_width=True):
        if selected_section != st.session_state.get('selected_tab', '📝 Analizar Contenido'):
            st.session_state.selected_tab = selected_section
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
    
    # Acciones rápidas directas
    st.subheader("⚡ Acciones Rápidas")
    
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("🔥 Tendencias", use_container_width=True):
            st.session_state.get_trends = True
            st.session_state.selected_tab = "📈 Trending Topics"
            st.rerun()
    
    with col_act2:
        if st.button("🎯 Ideas", use_container_width=True):
            st.session_state.get_quick_recs = True
            st.session_state.selected_tab = "🎯 Recomendaciones"
            st.rerun()
    
    st.markdown("---")
    st.caption("🔗 http://148.230.118.46:8501")
