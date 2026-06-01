import streamlit as st
import streamlit.components.v1 as components
import os
from app.auth import (
    get_current_user_name, get_current_user_email,
    get_current_user_role, logout_user, is_admin,
)


def save_session_to_browser():
    """
    Guarda el refresh_token en el localStorage del navegador.
    Se llama en cada render del sidebar para mantener la pulsera activa.
    """
    refresh_token = st.session_state.get("sb_refresh_token", "")
    if not refresh_token:
        return
    safe_token = refresh_token.replace("'", "\\'")
    components.html(
        f"<script>try{{localStorage.setItem('cm_rt','{safe_token}');}}catch(e){{}}</script>",
        height=0,
    )


def clear_session_from_browser():
    """Borra la pulsera del navegador al cerrar sesión."""
    components.html(
        "<script>try{localStorage.removeItem('cm_rt');}catch(e){}</script>",
        height=0,
    )


def render_sidebar():
    # Guardar pulsera en navegador en cada render (mantiene sesión actualizada)
    save_session_to_browser()

    with st.sidebar:
        # Logo
        logo_path = os.path.join("assets", "logo_sofgen.jpg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)

        st.markdown("---")

        # Navegación
        st.page_link("pages/1_Dashboard.py",     label="📊  Dashboard")
        st.page_link("pages/2_Cronograma.py",    label="📋  Cronograma")
        st.page_link("pages/3_Gantt.py",         label="📅  Gantt")
        st.page_link("pages/4_Configuracion.py", label="⚙️  Configuración")

        st.markdown("---")

        # Usuario
        name  = get_current_user_name()
        role  = get_current_user_role()
        role_label = "Administrador" if role == "admin" else "Usuario"

        st.markdown(f"""
<div style="padding:10px 4px;">
    <div style="font-size:13px;font-weight:600;color:#ffffff;">👤 {name}</div>
    <div style="font-size:11px;color:rgba(255,255,255,0.5);margin-top:2px;">{role_label}</div>
</div>
""", unsafe_allow_html=True)

        if st.button("Cerrar sesión", use_container_width=True, key="sidebar_logout"):
            clear_session_from_browser()
            logout_user()
            st.switch_page("main.py")


def render_page_header(title: str, subtitle: str = ""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def render_no_permission_warning():
    st.warning("🔒 Solo el administrador puede modificar estados de actividades.")
