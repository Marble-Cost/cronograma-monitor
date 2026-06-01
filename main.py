import streamlit as st
import os, base64

st.set_page_config(
    page_title="Compliance Monitor",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.auth import (
    is_authenticated, login_user, reset_password_for_email,
    logout_user, get_current_user_name, get_current_user_role,
)


# ──────────────────────────────────────────────────────────────
# Cargar logo (busca con guion y guion bajo)
# ──────────────────────────────────────────────────────────────
def load_logo():
    candidates = [
        "logo_sofgen.png", "logo_sofgen.jpg", "logo_sofgen.jpeg", "logo_sofgen.webp",
        "logo-sofgen.png", "logo-sofgen.jpg", "logo-sofgen.jpeg", "logo-sofgen.webp",
    ]
    for name in candidates:
        p = os.path.join("assets", name)
        if os.path.exists(p):
            ext = name.split(".")[-1]
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode(), ("png" if ext == "png" else "jpeg")
    return None, None


# ══════════════════════════════════════════════════════════════
# PANTALLA DE LOGIN (cuando NO hay sesión)
# ══════════════════════════════════════════════════════════════
def render_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    * { font-family: 'DM Sans', sans-serif !important; }
    #MainMenu, footer, [data-testid="stToolbar"], header { visibility: hidden !important; }
    section[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #002a52 0%, #003A70 60%, #004d94 100%) !important;
        min-height: 100vh !important;
    }
    .main { background: transparent !important; }
    .main .block-container {
        background: transparent !important;
        padding: 1rem !important;
        max-width: 440px !important;
        margin: 0 auto !important;
    }
    .stTextInput label, .stTextInput p {
        color: rgba(255,255,255,0.85) !important;
        font-weight: 500 !important; font-size: 13px !important;
        text-align: center !important; width: 100% !important;
    }
    .stTextInput input {
        border-radius: 8px !important;
        border: 1.5px solid rgba(255,255,255,0.2) !important;
        background: rgba(255,255,255,0.95) !important;
        padding: 8px 12px !important; font-size: 14px !important;
        text-align: center !important;
    }
    .stTextInput input:focus {
        border-color: #00B5B0 !important;
        box-shadow: 0 0 0 2px rgba(0,181,176,0.2) !important;
    }
    .stFormSubmitButton button, div[data-testid="stButton"] button {
        background: #00B5B0 !important; color: white !important;
        border: none !important; border-radius: 8px !important;
        font-weight: 700 !important; font-size: 14px !important; padding: 10px !important;
        width: 100% !important;
    }
    .stFormSubmitButton button:hover, div[data-testid="stButton"] button:hover {
        background: #009990 !important;
    }
    [data-testid="stForm"] { background: transparent !important; border: none !important; }
    [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
    </style>
    """, unsafe_allow_html=True)

    logo_data, mime = load_logo()
    if logo_data:
        st.markdown(
            f'<div style="text-align:center;margin:24px auto 22px auto;">'
            f'<img src="data:image/{mime};base64,{logo_data}" '
            f'style="width:100%;max-width:360px;border-radius:12px;background:white;'
            f'padding:14px 18px;box-shadow:0 4px 20px rgba(0,0,0,0.25);"></div>',
            unsafe_allow_html=True
        )

    st.markdown('<h2 style="text-align:center;color:white;font-size:23px;font-weight:700;margin:0 0 2px 0;letter-spacing:0.5px;">COMPLIANCE MONITOR</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#00B5B0;margin:0 0 18px 0;font-size:12px;font-weight:600;letter-spacing:3px;">— SCHEDULE —</p>', unsafe_allow_html=True)

    if "show_recovery" not in st.session_state:
        st.session_state.show_recovery = False
    if "recovery_sent" not in st.session_state:
        st.session_state.recovery_sent = False

    # ── Login ──────────────────────────────────────────────
    if not st.session_state.show_recovery:
        with st.form("login_form"):
            email    = st.text_input("Correo electrónico", placeholder="usuario@correo.com")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Ingresar al sistema", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("⚠️ Completa todos los campos.")
            else:
                with st.spinner("Verificando..."):
                    ok, err = login_user(email.strip(), password)
                if ok:
                    st.rerun()
                else:
                    st.error(f"🔒 Acceso denegado — {err}")

        if st.button("¿Olvidaste tu contraseña?", use_container_width=True, key="btn_recovery"):
            st.session_state.show_recovery = True
            st.rerun()

    # ── Recuperación ───────────────────────────────────────
    else:
        st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.6);margin:0 0 14px 0;font-size:13px;">Te enviaremos un correo para restablecer tu contraseña</p>', unsafe_allow_html=True)
        if not st.session_state.recovery_sent:
            with st.form("recovery_form"):
                rec_email = st.text_input("Tu correo electrónico", placeholder="usuario@correo.com")
                rec_btn   = st.form_submit_button("Enviar correo de recuperación", use_container_width=True)
            if rec_btn:
                if not rec_email:
                    st.error("⚠️ Ingresa tu correo electrónico.")
                else:
                    with st.spinner("Enviando..."):
                        ok, err = reset_password_for_email(rec_email.strip())
                    if ok:
                        st.session_state.recovery_sent = True
                        st.rerun()
                    else:
                        st.error(f"❌ Error — {err}")
        else:
            st.success("✅ Correo enviado. Revisa tu bandeja de entrada.")
            st.caption("Si no lo ves en unos minutos, revisa la carpeta de spam.")

        if st.button("← Volver al inicio de sesión", use_container_width=True, key="btn_back"):
            st.session_state.show_recovery = False
            st.session_state.recovery_sent = False
            st.rerun()

    st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.2);font-size:11px;margin-top:14px;">Cumplimiento Legal Corporativo · 2026</p>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR (cuando SÍ hay sesión)
# ══════════════════════════════════════════════════════════════
def render_sidebar_top():
    with st.sidebar:
        logo_data, mime = load_logo()
        if logo_data:
            st.markdown(
                f'<div style="text-align:center;padding:8px 0 12px 0;">'
                f'<img src="data:image/{mime};base64,{logo_data}" '
                f'style="width:100%;max-width:180px;border-radius:8px;background:white;padding:8px;"></div>',
                unsafe_allow_html=True
            )


def render_sidebar_bottom():
    with st.sidebar:
        st.markdown("---")
        name = get_current_user_name()
        role = get_current_user_role()
        role_label = "Administrador" if role == "admin" else "Usuario"
        st.markdown(
            f'<div style="padding:6px 4px;"><div style="font-size:13px;font-weight:600;color:#fff;">'
            f'👤 {name}</div><div style="font-size:11px;color:rgba(255,255,255,0.5);margin-top:2px;">'
            f'{role_label}</div></div>',
            unsafe_allow_html=True
        )
        if st.button("🚪 Cerrar sesión", use_container_width=True, key="sidebar_logout"):
            logout_user()
            st.rerun()


# ══════════════════════════════════════════════════════════════
# ENRUTADOR PRINCIPAL
# ══════════════════════════════════════════════════════════════
if not is_authenticated():
    render_login()
    st.stop()

# Hay sesión → mostrar navegación
render_sidebar_top()

dashboard   = st.Page("pages/1_Dashboard.py",     title="Dashboard",     icon=":material/dashboard:", default=True)
cronograma  = st.Page("pages/2_Cronograma.py",    title="Cronograma",    icon=":material/checklist:")
gantt       = st.Page("pages/3_Gantt.py",         title="Gantt",         icon=":material/calendar_month:")
config      = st.Page("pages/4_Configuracion.py", title="Configuración", icon=":material/settings:")

pg = st.navigation([dashboard, cronograma, gantt, config])

render_sidebar_bottom()

pg.run()
