import streamlit as st
import streamlit.components.v1 as components
import os, base64

st.set_page_config(
    page_title="Compliance Monitor · Sofgen Pharma",
    page_icon="🔵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from app.auth import login_user, is_authenticated, restore_session_from_token, reset_password_for_email

# ═══════════════════════════════════════════════════════════
# PASO 1: Verificar si hay un token de restauración en la URL
# (Lo coloca el navegador cuando detecta la pulsera guardada)
# ═══════════════════════════════════════════════════════════
restore_token = st.query_params.get("_rt", "")
if restore_token:
    # Limpiar el token de la URL inmediatamente
    st.query_params.clear()
    with st.spinner("Restaurando tu sesión..."):
        ok = restore_session_from_token(restore_token)
    if ok:
        st.switch_page("pages/1_Dashboard.py")
        st.stop()
    else:
        # Token expirado — borrar la pulsera del navegador
        components.html(
            "<script>try{localStorage.removeItem('cm_rt');}catch(e){}</script>",
            height=0,
        )

# ═══════════════════════════════════════════════════════════
# PASO 2: Si ya hay sesión activa, ir directo al Dashboard
# ═══════════════════════════════════════════════════════════
if is_authenticated():
    st.switch_page("pages/1_Dashboard.py")
    st.stop()

# ═══════════════════════════════════════════════════════════
# PASO 3: Sin sesión — inyectar JS que lee la pulsera del
# navegador y redirige con el token si existe
# ═══════════════════════════════════════════════════════════
components.html("""
<script>
(function() {
    try {
        var token = localStorage.getItem('cm_rt');
        if (token && !window.parent.location.search.includes('_rt=')) {
            setTimeout(function() {
                var url = window.parent.location.pathname + '?_rt=' + encodeURIComponent(token);
                window.parent.location.replace(url);
            }, 150);
        }
    } catch(e) {}
})();
</script>
""", height=0)

# ═══════════════════════════════════════════════════════════
# CSS del login
# ═══════════════════════════════════════════════════════════
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
    padding: 0.5rem 1rem !important;
    max-width: 420px !important;
    margin: 0 auto !important;
}
.stTextInput label, .stTextInput p {
    color: rgba(255,255,255,0.85) !important;
    font-weight: 500 !important; font-size: 13px !important;
}
.stTextInput input {
    border-radius: 8px !important;
    border: 1.5px solid rgba(255,255,255,0.2) !important;
    background: rgba(255,255,255,0.95) !important;
    padding: 8px 12px !important; font-size: 14px !important;
}
.stTextInput input:focus {
    border-color: #00B5B0 !important;
    box-shadow: 0 0 0 2px rgba(0,181,176,0.2) !important;
}
.stFormSubmitButton button {
    background: #00B5B0 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; font-size: 14px !important; padding: 10px !important;
}
.stFormSubmitButton button:hover { background: #009990 !important; }
[data-testid="stForm"] { background: transparent !important; border: none !important; }
[data-testid="stVerticalBlock"] { gap: 0.25rem !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# Logo
# ═══════════════════════════════════════════════════════════
def load_logo():
    p = os.path.join("assets", "logo_sofgen.jpg")
    if os.path.exists(p):
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo = load_logo()

if logo:
    st.markdown(
        f'<div style="text-align:center;margin-bottom:14px;margin-top:10px;">'
        f'<img src="data:image/jpeg;base64,{logo}" width="100" '
        f'style="border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.3);"></div>',
        unsafe_allow_html=True
    )

# ═══════════════════════════════════════════════════════════
# Estado de pantalla
# ═══════════════════════════════════════════════════════════
if "show_recovery" not in st.session_state:
    st.session_state.show_recovery = False
if "recovery_sent" not in st.session_state:
    st.session_state.recovery_sent = False

# ═══════════════════════════════════════════════════════════
# Pantalla de login
# ═══════════════════════════════════════════════════════════
if not st.session_state.show_recovery:
    st.markdown('<h2 style="text-align:center;color:white;font-size:22px;font-weight:700;margin:0 0 2px 0;">Compliance Monitor</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.5);margin:0 0 14px 0;font-size:13px;">Sofgen Pharma · Ingresa tus credenciales</p>', unsafe_allow_html=True)

    with st.form("login_form"):
        email    = st.text_input("Correo electrónico", placeholder="usuario@sofgen.com")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Ingresar al sistema", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("⚠️ Completa todos los campos.")
        else:
            with st.spinner("Verificando..."):
                ok, err = login_user(email.strip(), password)
            if ok:
                st.switch_page("pages/1_Dashboard.py")
            else:
                st.error(f"🔒 Acceso denegado — {err}")

    if st.button("¿Olvidaste tu contraseña?", use_container_width=True, key="btn_recovery"):
        st.session_state.show_recovery = True
        st.rerun()

# ═══════════════════════════════════════════════════════════
# Pantalla de recuperación
# ═══════════════════════════════════════════════════════════
else:
    st.markdown('<h2 style="text-align:center;color:white;font-size:20px;font-weight:700;margin:0 0 4px 0;">Recuperar contraseña</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.5);margin:0 0 14px 0;font-size:13px;">Te enviaremos un correo para restablecer tu contraseña</p>', unsafe_allow_html=True)

    if not st.session_state.recovery_sent:
        with st.form("recovery_form"):
            rec_email = st.text_input("Tu correo electrónico", placeholder="usuario@sofgen.com")
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

    if st.button("← Volver al inicio de sesión", use_container_width=True, key="btn_back"):
        st.session_state.show_recovery = False
        st.session_state.recovery_sent = False
        st.rerun()

st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.2);font-size:11px;margin-top:10px;">Cumplimiento Legal Corporativo · 2026</p>', unsafe_allow_html=True)
