import streamlit as st
import os
from app.auth import (
    get_current_user_name, get_current_user_email,
    get_current_user_role, logout_user, is_admin,
)
from app.database import get_project_config
from app.utils import format_date_es


def render_sidebar():
    with st.sidebar:
        # Logo
        logo_path = os.path.join("assets", "logo_sofgen.jpg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
        else:
            st.markdown("### Compliance Monitor")

        st.divider()

        # Info proyecto
        try:
            config   = get_project_config()
            scenario = config.scenario
            sd       = config.start_date
        except Exception:
            scenario = "—"
            sd       = None

        st.markdown(f"""
        **Escenario activo**  
        {scenario}
        
        **Fecha inicio**  
        {format_date_es(sd)}
        """)

        st.divider()

        # Navegación manual (evita que aparezca "main" en el menú)
        st.page_link("pages/1_Dashboard.py",     label="📊 Dashboard")
        st.page_link("pages/2_Cronograma.py",    label="📋 Cronograma")
        st.page_link("pages/3_Gantt.py",         label="📅 Gantt")
        st.page_link("pages/4_Configuracion.py", label="⚙️ Configuración")

        st.divider()

        # Usuario
        name  = get_current_user_name()
        email = get_current_user_email() or ""
        role  = get_current_user_role()

        st.markdown(f"👤 **{name}**  \n{email}  \n`{role}`")

        if st.button("🚪 Cerrar sesión", use_container_width=True, key="sidebar_logout"):
            logout_user()
            st.switch_page("main.py")


def kpi_card(value, label: str, subtitle: str, color_class: str = "kpi-teal", icon: str = "") -> str:
    return f"""
    <div class="kpi-card {color_class}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-sub">{subtitle}</div>
    </div>
    """


def render_page_header(title: str, subtitle: str = ""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def render_no_permission_warning():
    st.warning("🔒 Solo el administrador puede modificar estados de actividades.")
