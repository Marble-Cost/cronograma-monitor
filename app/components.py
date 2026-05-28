import streamlit as st
import os
from app.auth import (
    get_current_user_name, get_current_user_email,
    get_current_user_role, logout_user, is_admin,
)


def render_sidebar():
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

        # Usuario — nombre completo, no correo
        name = get_current_user_name()
        role = get_current_user_role()
        role_label = "Administrador" if role == "admin" else "Usuario"

        st.markdown(f"""
<div style="padding:10px 4px;">
    <div style="font-size:13px;font-weight:600;color:#ffffff;">👤 {name}</div>
    <div style="font-size:11px;color:rgba(255,255,255,0.5);margin-top:2px;">{role_label}</div>
</div>
""", unsafe_allow_html=True)

        if st.button("Cerrar sesión", use_container_width=True, key="sidebar_logout"):
            logout_user()
            st.switch_page("main.py")


def render_page_header(title: str, subtitle: str = ""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def render_no_permission_warning():
    st.warning("🔒 Solo el administrador puede modificar estados de actividades.")
