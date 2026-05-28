import streamlit as st
import os
import base64

st.set_page_config(
    page_title="Compliance Monitor · Sofgen Pharma",
    page_icon="🔵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from app.auth import login_user, is_authenticated, _restore_from_cookie

# Intentar restaurar sesión desde cookie antes de mostrar login
if is_authenticated() or _restore_from_cookie():
    st.switch_page("pages/1_Dashboard.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');
* { font-family: 'DM Sans', sans-serif !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.stApp { background: linear-gradient(135deg, #002a52 0%, #003A70 50%, #004d94 100%) !important; }
.main .block-container { padding: 2rem 1rem !important; max-width: 480px !important; }
.stTextInput input {
    border-radius: 8px !important;
    border: 1.5px solid #E2E8F0 !important;
    font-size: 14px !important;
}
.stTextInput input:focus {
    border-color: #00B5B0 !important;
    box-shadow: 0 0 0 3px rgba(0,181,176,0.12) !important;
}
.stFormSubmitButton button {
    background: #003A70 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px !important;
    width: 100% !important;
}
.stFormSubmitButton button:hover { background: #00B5B0 !important; }
</style>
""", unsafe_allow_html=True)


def load_logo_b64():
    path = os.path.join("assets", "logo_sofgen.jpg")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


logo_b64 = load_logo_b64()

if logo_b64:
    st.markdown(
        f'<div style="text-align:center;margin-bottom:24px;">'
        f'<img src="data:image/jpeg;base64,{logo_b64}" width="160"></div>',
        unsafe_allow_html=True
    )

st.markdown('<h2 style="text-align:center;color:white;margin-bottom:4px;">Compliance Monitor</h2>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.6);margin-bottom:28px;font-size:14px;">Ingresa tus credenciales para continuar</p>', unsafe_allow_html=True)

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

st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.35);font-size:12px;margin-top:24px;">Sofgen Pharma · Cumplimiento Legal Corporativo · 2026</p>', unsafe_allow_html=True)
