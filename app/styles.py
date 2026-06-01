import streamlit as st

SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');
* { font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

/* ── Sidebar siempre oscuro ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
section[data-testid="stSidebar"] {
    background-color: #003A70 !important;
}
[data-testid="stSidebarNav"] { display: none !important; }

/* Texto sidebar */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }

/* Links de navegación */
[data-testid="stSidebar"] a {
    color: rgba(255,255,255,0.75) !important;
    text-decoration: none !important;
    display: block;
    padding: 8px 12px;
    border-radius: 8px;
    margin: 2px 0;
    transition: all 0.2s;
}
[data-testid="stSidebar"] a:hover { background: rgba(0,181,176,0.18) !important; color: #00B5B0 !important; }
[data-testid="stSidebar"] a[aria-current="page"] { background: rgba(0,181,176,0.22) !important; color: #00B5B0 !important; border-left: 3px solid #00B5B0; }

/* Botón cerrar sesión en sidebar */
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.7) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(239,68,68,0.2) !important;
    color: #FCA5A5 !important;
    border-color: rgba(239,68,68,0.3) !important;
}

/* Divider sidebar */
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }

/* ── Contenido principal ── */
.main .block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1400px !important; }
h1 { color: #003A70 !important; font-weight: 700 !important; }
h2, h3 { color: #003A70 !important; font-weight: 600 !important; }

/* Métricas */
[data-testid="stMetricValue"] { color: #003A70 !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #64748B !important; }

/* Botones principales */
.stButton > button {
    background: #003A70 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton > button:hover { background: #00B5B0 !important; }

/* Inputs */
.stTextInput input { border-radius: 8px !important; border: 1.5px solid #E2E8F0 !important; }
.stTextInput input:focus { border-color: #00B5B0 !important; box-shadow: 0 0 0 3px rgba(0,181,176,0.12) !important; }

/* Tabs */
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #003A70 !important; border-bottom: 2px solid #00B5B0 !important; }

/* DataFrame */
[data-testid="stDataFrame"], [data-testid="data-editor"] { border-radius: 10px !important; border: 1px solid #E2E8F0 !important; }
</style>
"""

def inject_global_css():
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
