import streamlit as st


# ──────────────────────────────────────────────────────────────
# COMPLIANCE MONITOR · Design System
# Paleta Sofgen Pharma: #003A70 (Navy) · #00B5B0 (Turquoise)
# ──────────────────────────────────────────────────────────────

def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=DM+Mono:wght@400;500&display=swap');

    /* ── Base ───────────────────────────────────────────── */
    html, body, [class*="css"], * {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { visibility: hidden; }

    /* ── Sidebar ─────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background-color: #003A70 !important;
        border-right: none !important;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #003A70 !important;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span:not([data-testid]),
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: rgba(255,255,255,0.85) !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    /* Nav links */
    [data-testid="stSidebarNav"] a {
        color: rgba(255,255,255,0.7) !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        margin: 2px 4px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(0,181,176,0.15) !important;
        color: #00B5B0 !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"],
    [data-testid="stSidebarNav"] a.active {
        background: rgba(0,181,176,0.2) !important;
        color: #00B5B0 !important;
        border-left: 3px solid #00B5B0 !important;
    }
    [data-testid="stSidebarNav"] span {
        color: inherit !important;
    }
    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.1) !important;
        color: rgba(255,255,255,0.85) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        transition: all 0.2s !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(239,68,68,0.15) !important;
        border-color: rgba(239,68,68,0.4) !important;
        color: #FCA5A5 !important;
    }
    /* Sidebar select */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border-color: rgba(255,255,255,0.2) !important;
    }

    /* ── Main Layout ─────────────────────────────────────── */
    .main .block-container {
        padding: 1.5rem 2rem 2rem 2rem !important;
        max-width: 1400px !important;
    }

    /* ── Page Header ─────────────────────────────────────── */
    .page-header {
        margin-bottom: 24px;
    }
    .page-title {
        font-size: 26px;
        font-weight: 700;
        color: #003A70;
        margin: 0 0 4px 0;
        letter-spacing: -0.3px;
    }
    .page-subtitle {
        font-size: 14px;
        color: #64748B;
        margin: 0;
    }

    /* ── KPI Cards ───────────────────────────────────────── */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px 22px 18px 22px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
        height: 100%;
        transition: box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        box-shadow: 0 4px 16px rgba(0,58,112,0.1);
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 14px 14px 0 0;
    }
    .kpi-card.kpi-navy::after    { background: #003A70; }
    .kpi-card.kpi-teal::after    { background: #00B5B0; }
    .kpi-card.kpi-success::after { background: #00B050; }
    .kpi-card.kpi-warning::after { background: #F59E0B; }
    .kpi-card.kpi-gray::after    { background: #94A3B8; }
    .kpi-icon {
        font-size: 20px;
        margin-bottom: 10px;
        display: block;
    }
    .kpi-value {
        font-size: 40px;
        font-weight: 700;
        color: #003A70;
        line-height: 1;
        margin-bottom: 4px;
        letter-spacing: -1px;
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B;
        margin-bottom: 2px;
    }
    .kpi-sub {
        font-size: 12px;
        color: #94A3B8;
    }

    /* ── Section Headers ─────────────────────────────────── */
    .section-title {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #003A70;
        margin: 28px 0 14px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #E2E8F0;
    }

    /* ── Status Badges ───────────────────────────────────── */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        white-space: nowrap;
    }
    .badge-pendiente  { background: #F1F5F9; color: #64748B; }
    .badge-progreso   { background: #FFFBEB; color: #D97706; }
    .badge-completado { background: #F0FDF4; color: #16A34A; }

    /* ── Semáforo ────────────────────────────────────────── */
    .semaforo-dot {
        display: inline-block;
        width: 10px; height: 10px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .sem-pending  { background: #CBD5E1; }
    .sem-progress { background: #F59E0B; }
    .sem-done     { background: #22C55E; }

    /* ── Progress Bar (custom) ───────────────────────────── */
    .progress-track {
        background: #F1F5F9;
        border-radius: 6px;
        height: 7px;
        overflow: hidden;
        flex: 1;
    }
    .progress-fill {
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, #00B5B0, #003A70);
        transition: width 0.5s ease;
    }
    .progress-fill.done { background: #22C55E; }

    /* ── Phase Table ─────────────────────────────────────── */
    .phase-table { width: 100%; border-collapse: collapse; }
    .phase-table th {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #94A3B8;
        padding: 8px 12px;
        border-bottom: 1px solid #E2E8F0;
        text-align: left;
    }
    .phase-table td {
        padding: 12px 12px;
        border-bottom: 1px solid #F8FAFC;
        font-size: 13px;
        color: #374151;
        vertical-align: middle;
    }
    .phase-table tr:hover td { background: #F8FAFC; }
    .fase-name { font-weight: 600; color: #003A70; }
    .progress-row { display: flex; align-items: center; gap: 10px; }
    .progress-pct { font-size: 12px; font-weight: 600; color: #003A70; min-width: 36px; text-align: right; }

    /* ── Sidebar User Card ───────────────────────────────── */
    .sidebar-user-card {
        background: rgba(0,181,176,0.12);
        border: 1px solid rgba(0,181,176,0.25);
        border-radius: 10px;
        padding: 12px 14px;
        margin: 8px 0;
    }
    .sidebar-user-name {
        font-size: 13px;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 2px;
    }
    .sidebar-user-email {
        font-size: 11px;
        color: rgba(255,255,255,0.55);
    }
    .sidebar-role-badge {
        display: inline-block;
        background: rgba(0,181,176,0.25);
        color: #00B5B0;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 2px 8px;
        border-radius: 10px;
        margin-top: 4px;
    }
    .sidebar-separator {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.12);
        margin: 10px 0;
    }

    /* ── Buttons ─────────────────────────────────────────── */
    .stButton > button {
        background: #003A70 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 8px 20px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: #00B5B0 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,181,176,0.3) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── Form inputs ─────────────────────────────────────── */
    .stTextInput input, .stSelectbox select {
        border-radius: 8px !important;
        border-color: #CBD5E1 !important;
    }
    .stTextInput input:focus { border-color: #00B5B0 !important; box-shadow: 0 0 0 3px rgba(0,181,176,0.15) !important; }
    .stSelectbox label, .stTextInput label, .stDateInput label, .stRadio label {
        font-weight: 500 !important;
        color: #374151 !important;
        font-size: 14px !important;
    }

    /* ── Alert / Info boxes ──────────────────────────────── */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px !important;
    }
    .info-box {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 10px;
        padding: 14px 16px;
        font-size: 13px;
        color: #1E40AF;
    }
    .warning-box {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 10px;
        padding: 14px 16px;
        font-size: 13px;
        color: #92400E;
    }

    /* ── Headings override ───────────────────────────────── */
    h1 { color: #003A70 !important; font-weight: 700 !important; letter-spacing: -0.5px !important; }
    h2 { color: #003A70 !important; font-weight: 600 !important; }
    h3 { color: #1E293B !important; font-weight: 600 !important; }

    /* ── Dataframe/editor ────────────────────────────────── */
    [data-testid="stDataFrame"], [data-testid="data-editor"] {
        border-radius: 10px !important;
        overflow: hidden !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* ── Metric boxes ────────────────────────────────────── */
    [data-testid="stMetricValue"] {
        color: #003A70 !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-weight: 500 !important;
    }

    /* ── Tabs ────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #E2E8F0 !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600 !important;
        color: #64748B !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 18px !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #003A70 !important;
        border-bottom: 2px solid #00B5B0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def inject_login_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

    html, body, * { font-family: 'DM Sans', sans-serif !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { visibility: hidden; }

    /* Hide sidebar on login */
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Left panel */
    .login-left {
        background: linear-gradient(160deg, #003A70 0%, #005299 60%, #003A70 100%);
        min-height: 100vh;
        padding: 60px 50px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }
    .login-left::before {
        content: '';
        position: absolute;
        top: -100px; right: -100px;
        width: 350px; height: 350px;
        background: radial-gradient(circle, rgba(0,181,176,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .login-left::after {
        content: '';
        position: absolute;
        bottom: -80px; left: -80px;
        width: 280px; height: 280px;
        background: radial-gradient(circle, rgba(0,181,176,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    .login-app-name {
        font-size: 32px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    .login-app-desc {
        font-size: 16px;
        color: rgba(255,255,255,0.65);
        margin-bottom: 48px;
        line-height: 1.5;
    }
    .login-feature {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .login-feature:last-of-type { border-bottom: none; }
    .login-feature-icon {
        width: 40px; height: 40px;
        background: rgba(0,181,176,0.2);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }
    .login-feature-text {
        font-size: 14px;
        color: rgba(255,255,255,0.8);
        line-height: 1.4;
    }
    .login-feature-text strong { color: #FFFFFF; }
    .login-footer {
        margin-top: auto;
        padding-top: 40px;
        font-size: 12px;
        color: rgba(255,255,255,0.35);
    }

    /* Right panel */
    .login-right {
        background: #FFFFFF;
        min-height: 100vh;
        padding: 60px 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .login-logo-wrap { margin-bottom: 36px; }
    .login-title {
        font-size: 26px;
        font-weight: 700;
        color: #003A70;
        margin-bottom: 6px;
    }
    .login-subtitle {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 32px;
    }
    .login-help {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
