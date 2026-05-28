import streamlit as st
import os, base64

st.set_page_config(
    page_title="Compliance Monitor · Sofgen Pharma",
    page_icon="🔵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from app.auth import login_user, is_authenticated

if is_authenticated():
    st.switch_page("pages/1_Dashboard.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
* { font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, [data-testid="stToolbar"], header { visibility: hidden !important; }
section[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #002a52 0%, #003A70 60%, #004d94 100%) !important;
    height: 100vh !important;
    overflow: hidden !important;
}
.main { background: transparent !important; }
.main .block-container {
    background: transparent !important;
    padding: 0.5rem 1rem !important;
    max-width: 400px !important;
    margin: 0 auto !important;
}

.stTextInput label, .stTextInput p {
    color: rgba(255,255,255,0.85) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    margin-bottom: 2px !important;
}
.stTextInput > div { margin-bottom: 4px !important; }
.stTextInput input {
    border-radius: 8px !important;
    border: 1.5px solid rgba(255,255,255,0.2) !important;
    background: rgba(255,255,255,0.95) !important;
    padding: 8px 12px !important;
    font-size: 14px !important;
}
.stTextInput input:focus {
    border-color: #00B5B0 !important;
    box-shadow: 0 0 0 2px rgba(0,181,176,0.2) !important;
}
.stFormSubmitButton button {
    background: #00B5B0 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; font-size: 14px !important;
    padding: 10px !important; margin-top: 4px !important;
}
.stFormSubmitButton button:hover { background: #009990 !important; }
[data-testid="stForm"] { background: transparent !important; border: none !important; }
[data-testid="stVerticalBlock"] { gap: 0.3rem !important; }
</style>
""", unsafe_allow_html=True)

def load_logo():
    p = os.path.join("assets", "logo_sofgen.jpg")
    if os.path.exists(p):
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo = load_logo()

if logo:
    st.markdown(
        f'<div style="text-align:center;margin-bottom:12px;margin-top:8px;">'
        f'<img src="data:image/jpeg;base64,{logo}" width="100" '
        f'style="border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.3);">'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown('<h2 style="text-align:center;color:white;font-size:22px;font-weight:700;margin:0 0 4px 0;">Compliance Monitor</h2>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.5);margin:0 0 16px 0;font-size:13px;">Sofgen Pharma · Ingresa tus credenciales para continuar</p>', unsafe_allow_html=True)

with st.form("login_form"):
    email    = st.text_input("Correo electrónico", placeholder="usuario@sofgen.com")
    password = st.text_input("Contraseña", type="password", placeholder="••••••••")
    submitted = st.form_submit_button("Ingresar al sistema", use_container_width=True)

if submitted:
    if not email or not password:
        st.error("⚠️ Por favor completa todos los campos.")
    else:
        with st.spinner("Verificando..."):
            ok, err = login_user(email.strip(), password)
        if ok:
            st.switch_page("pages/1_Dashboard.py")
        else:
            st.error(f"🔒 Acceso denegado — {err}")

st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.2);font-size:11px;margin-top:12px;">Cumplimiento Legal Corporativo · 2026</p>', unsafe_allow_html=True)
