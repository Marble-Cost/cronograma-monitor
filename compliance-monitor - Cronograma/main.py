import streamlit as st
import os
import base64

st.set_page_config(
    page_title="Compliance Monitor · Sofgen Pharma",
    page_icon="🔵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from app.auth import login_user, is_authenticated

# ── Redirigir si ya está autenticado ─────────────────────────
if is_authenticated():
    st.switch_page("pages/1_Dashboard.py")

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');
* { font-family: 'DM Sans', sans-serif !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Fondo navy en toda la página */
.stApp {
    background: linear-gradient(135deg, #002a52 0%, #003A70 50%, #004d94 100%) !important;
}
.main .block-container {
    padding: 2rem 1rem !important;
    max-width: 480px !important;
}

/* Tarjeta blanca del formulario */
.login-card {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 40px 36px;
    box-shadow: 0 24px 80px rgba(0,0,0,0.25);
}
.login-logo-wrap { text-align: center; margin-bottom: 24px; }
.login-title {
    font-size: 24px;
    font-weight: 700;
    color: #003A70;
    margin-bottom: 4px;
    text-align: center;
}
.login-subtitle {
    font-size: 14px;
    color: #64748B;
    margin-bottom: 28px;
    text-align: center;
}
.login-divider {
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 20px 0;
}
.login-feature-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
}
.login-feature-icon {
    font-size: 16px;
    min-width: 24px;
    text-align: center;
}
.login-feature-text {
    font-size: 12px;
    color: #64748B;
    line-height: 1.4;
}
.login-footer-text {
    text-align: center;
    font-size: 11px;
    color: rgba(255,255,255,0.45);
    margin-top: 20px;
}

/* Inputs dentro de la tarjeta */
.stTextInput input {
    border-radius: 8px !important;
    border: 1.5px solid #E2E8F0 !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus {
    border-color: #00B5B0 !important;
    box-shadow: 0 0 0 3px rgba(0,181,176,0.12) !important;
}
.stTextInput label { color: #374151 !important; font-weight: 500 !important; font-size: 13px !important; }

/* Botón de submit */
.stFormSubmitButton button {
    background: #003A70 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stFormSubmitButton button:hover {
    background: #00B5B0 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,181,176,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Logo ──────────────────────────────────────────────────────
def load_logo_b64():
    path = os.path.join("assets", "logo_sofgen.jpg")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = load_logo_b64()

# ── Tarjeta de login ──────────────────────────────────────────
logo_html = (
    f'<div class="login-logo-wrap"><img src="data:image/jpeg;base64,{logo_b64}" width="160"></div>'
    if logo_b64 else
    '<div class="login-logo-wrap" style="font-size:22px;font-weight:700;color:#003A70;">Sofgen Pharma</div>'
)

st.markdown(f"""
<div class="login-card">
    {logo_html}
    <div class="login-title">Compliance Monitor</div>
    <div class="login-subtitle">Ingresa tus credenciales corporativas para continuar</div>
</div>
""", unsafe_allow_html=True)

# ── Formulario (widgets nativos de Streamlit) ─────────────────
with st.form("login_form"):
    email    = st.text_input("Correo electrónico", placeholder="usuario@sofgen.com")
    password = st.text_input("Contraseña", type="password", placeholder="••••••••")
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Ingresar al sistema", use_container_width=True)

if submitted:
    if not email or not password:
        st.error("⚠️ Por favor completa todos los campos.")
    else:
        with st.spinner("Verificando credenciales..."):
            ok, err = login_user(email.strip(), password)
        if ok:
            st.success("✅ ¡Acceso concedido!")
            st.switch_page("pages/1_Dashboard.py")
        else:
            st.error(f"🔒 Acceso denegado — {err}")

# ── Features y footer ─────────────────────────────────────────
st.markdown("""
<div style="background:rgba(255,255,255,0.06);border-radius:14px;padding:16px 20px;margin-top:16px;">
    <div class="login-feature-row">
        <div class="login-feature-icon">📊</div>
        <div class="login-feature-text"><strong style="color:rgba(255,255,255,0.85);">Dashboard en tiempo real</strong> — KPIs y semáforos por fase</div>
    </div>
    <div class="login-feature-row">
        <div class="login-feature-icon">📅</div>
        <div class="login-feature-text"><strong style="color:rgba(255,255,255,0.85);">Gantt interactivo · 12 semanas</strong> — 25 actividades en 5 fases</div>
    </div>
    <div class="login-feature-row">
        <div class="login-feature-icon">🔐</div>
        <div class="login-feature-text"><strong style="color:rgba(255,255,255,0.85);">Roles y permisos</strong> — Analista · Supervisor · Administrador</div>
    </div>
    <div class="login-feature-row">
        <div class="login-feature-icon">☁️</div>
        <div class="login-feature-text"><strong style="color:rgba(255,255,255,0.85);">Datos persistentes</strong> — Todo se conserva al volver a ingresar</div>
    </div>
</div>
<div class="login-footer-text">Sofgen Pharma · Cumplimiento Legal Corporativo · 2026</div>
""", unsafe_allow_html=True)
