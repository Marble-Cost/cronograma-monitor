import streamlit as st
import os
import base64
from app.auth import (
    get_current_user_name, get_current_user_email,
    get_current_user_role, logout_user,
)
from app.database import get_project_config
from app.models import SEMAFORO


def render_sidebar():
    """Renderiza el sidebar completo con logo, info del proyecto y usuario."""
    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────
        logo_path = os.path.join("assets", "logo_sofgen.jpg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=160)
        else:
            st.markdown("### Compliance Monitor")

        st.markdown('<hr class="sidebar-separator">', unsafe_allow_html=True)

        # ── Info proyecto ─────────────────────────────────────
        try:
            config = get_project_config()
            scenario = config.scenario
            sd = config.start_date
        except Exception:
            scenario = "—"
            sd = None

        from app.utils import format_date_es
        st.markdown(f"""
        <div style="padding: 4px 0 10px 0;">
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.07em;color:rgba(255,255,255,0.4);margin-bottom:6px;">
                Proyecto activo
            </div>
            <div style="font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:4px;">
                Compliance Monitor
            </div>
            <div style="font-size:12px;color:rgba(255,255,255,0.55);">
                Sofgen Pharma · 12 semanas
            </div>
            <div style="margin-top:8px;display:flex;gap:6px;align-items:center;">
                <span style="background:rgba(0,181,176,0.2);color:#00B5B0;font-size:11px;
                             font-weight:600;padding:2px 8px;border-radius:10px;">
                    {scenario}
                </span>
            </div>
            <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:6px;">
                Inicio: {format_date_es(sd)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr class="sidebar-separator">', unsafe_allow_html=True)

        # ── Navegación automática de Streamlit queda aquí ────
        # (Streamlit inserta los links de navegación automáticamente)

        st.markdown('<hr class="sidebar-separator" style="margin-top:auto;">', unsafe_allow_html=True)

        # ── Usuario ───────────────────────────────────────────
        name  = get_current_user_name()
        email = get_current_user_email() or ""
        role  = get_current_user_role()

        st.markdown(f"""
        <div class="sidebar-user-card">
            <div class="sidebar-user-name">👤 {name}</div>
            <div class="sidebar-user-email">{email}</div>
            <div class="sidebar-role-badge">{role}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Cerrar sesión", use_container_width=True, key="sidebar_logout"):
            logout_user()
            st.switch_page("main.py")


def kpi_card(value, label: str, subtitle: str, color_class: str = "kpi-teal", icon: str = "") -> str:
    """Genera HTML de una tarjeta KPI."""
    return f"""
    <div class="kpi-card {color_class}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-sub">{subtitle}</div>
    </div>
    """


def status_badge(status: str) -> str:
    from app.models import STATUS_BADGE_CSS
    css = STATUS_BADGE_CSS.get(status, "badge-pendiente")
    return f'<span class="badge {css}">{status}</span>'


def progress_bar_html(pct: int, done: bool = False) -> str:
    fill_class = "progress-fill done" if done else "progress-fill"
    width = max(0, min(100, pct))
    return f"""
    <div class="progress-row">
        <div class="progress-track">
            <div class="{fill_class}" style="width:{width}%"></div>
        </div>
        <div class="progress-pct">{pct}%</div>
    </div>
    """


def semaforo_html(phase_data: dict) -> str:
    from app.utils import semaforo_fase
    emoji, label = semaforo_fase(phase_data)
    return f"{emoji} {label}"


def render_page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">{title}</div>
        {"" if not subtitle else f'<div class="page-subtitle">{subtitle}</div>'}
    </div>
    """, unsafe_allow_html=True)


def render_no_permission_warning():
    st.markdown("""
    <div class="warning-box">
        🔒 <strong>Acceso restringido</strong> — Solo supervisores y administradores
        pueden modificar estados de actividades. Contacta a tu supervisor para actualizar el cronograma.
    </div>
    """, unsafe_allow_html=True)
