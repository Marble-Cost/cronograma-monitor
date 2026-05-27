import streamlit as st
import os
import base64

st.set_page_config(
    page_title="Compliance Monitor · Sofgen Pharma",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from app.auth import login_user, is_authenticated
from app.styles import inject_login_css

inject_login_css()

# ── Redirigir si ya está autenticado ─────────────────────────
if is_authenticated():
    st.switch_page("pages/1_Dashboard.py")


def load_logo_b64() -> str | None:
    path = os.path.join("assets", "logo_sofgen.jpg")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


logo_b64 = load_logo_b64()

# ── Layout: dos columnas ─────────────────────────────────────
col_left, col_right = st.columns([1.1, 0.9], gap="small")

# ── Panel izquierdo (branding) ────────────────────────────────
with col_left:
    st.markdown(f"""
    <div class="login-left">
        <div style="position:relative;z-index:1;">
            <div class="login-app-name">Compliance Monitor</div>
            <div class="login-app-desc">
                Sistema de Gestión de Cronograma Corporativo<br>
                <span style="color:rgba(255,255,255,0.45);font-size:14px;">Sofgen Pharma · Despliegue 2026</span>
            </div>

            <div class="login-feature">
                <div class="login-feature-icon">📊</div>
                <div class="login-feature-text">
                    <strong>Dashboard en tiempo real</strong><br>
                    KPIs, semáforos por fase y progreso global del proyecto
                </div>
            </div>
            <div class="login-feature">
                <div class="login-feature-icon">📅</div>
                <div class="login-feature-text">
                    <strong>Cronograma Gantt · 12 semanas</strong><br>
                    25 actividades en 5 fases. Fechas automáticas desde fecha inicio
                </div>
            </div>
            <div class="login-feature">
                <div class="login-feature-icon">🔐</div>
                <div class="login-feature-text">
                    <strong>Roles y permisos</strong><br>
                    Analista · Supervisor · Administrador con acceso diferenciado
                </div>
            </div>
            <div class="login-feature">
                <div class="login-feature-icon">☁️</div>
                <div class="login-feature-text">
                    <strong>Memoria persistente</strong><br>
                    Datos en Supabase. Todo se conserva al recargar o regresar
                </div>
            </div>

            <div class="login-footer">
                Versión Mayo 2026 · Cumplimiento Legal Corporativo
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Panel derecho (formulario) ────────────────────────────────
with col_right:
    st.markdown('<div class="login-right">', unsafe_allow_html=True)

    # Logo
    if logo_b64:
        st.markdown(
            f'<div class="login-logo-wrap"><img src="data:image/jpeg;base64,{logo_b64}" width="180"></div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="login-title">Bienvenido</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Ingresa tus credenciales para continuar</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Formulario
    with st.form("login_form", clear_on_submit=False):
        email    = st.text_input("Correo electrónico", placeholder="usuario@sofgen.com")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "Ingresar al sistema",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        if not email or not password:
            st.error("⚠️ Por favor completa todos los campos.")
        else:
            with st.spinner("Verificando credenciales..."):
                ok, err = login_user(email.strip(), password)
            if ok:
                st.success("✅ ¡Acceso concedido! Cargando dashboard...")
                st.switch_page("pages/1_Dashboard.py")
            else:
                st.error(f"🔒 Acceso denegado — {err}")

    st.markdown("""
    <div class="login-help">
        ¿Problemas para acceder? Contacta al administrador del sistema<br>
        o escribe a <strong>cumplimiento@sofgen.com</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
