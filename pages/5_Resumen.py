import streamlit as st

st.set_page_config(
    page_title="Resumen Ejecutivo · Compliance Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from app.auth import require_auth
from app.styles import inject_global_css
from app.components import render_sidebar
from app.database import get_kpis, get_phase_progress, get_project_config, get_activities
from app.utils import get_current_week, format_date_es

require_auth()
inject_global_css()
render_sidebar()

config       = get_project_config()
start_date   = config.start_date
current_week = get_current_week(start_date)

# ── Selector de escenario ─────────────────────────────────────
scenario = config.scenario  # Compliance Monitor

kpis           = get_kpis(scenario)
phase_progress = get_phase_progress(scenario)
all_acts       = get_activities(scenario)

# ── Salud ─────────────────────────────────────────────────────
if kpis.pct_completed >= 100:
    salud_icon, salud_label, salud_bg, salud_fg = "🏆", "PROYECTO COMPLETADO", "#DCFCE7", "#16A34A"
elif current_week:
    expected = (current_week / 12) * 100
    diff     = kpis.pct_completed - expected
    if diff >= 0:
        salud_icon, salud_label, salud_bg, salud_fg = "🟢", "EN TIEMPO", "#DCFCE7", "#16A34A"
    elif diff >= -15:
        salud_icon, salud_label, salud_bg, salud_fg = "🟡", "LIGERAMENTE ATRASADO", "#FEF9C3", "#D97706"
    else:
        salud_icon, salud_label, salud_bg, salud_fg = "🔴", "EN RIESGO", "#FEE2E2", "#DC2626"
else:
    salud_icon, salud_label, salud_bg, salud_fg = "⏸", "SIN FECHA DE INICIO", "#F1F5F9", "#64748B"

# ── CSS limpio para modo reunión ──────────────────────────────
st.markdown("""
<style>
.resumen-header {
    background: #003A70;
    color: white;
    border-radius: 12px;
    padding: 22px 32px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.resumen-pct {
    font-size: 64px;
    font-weight: 800;
    color: #00B5B0;
    line-height: 1;
}
.salud-box {
    border-radius: 10px;
    padding: 14px 24px;
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 20px;
}
.fase-row {
    background: #F8FAFC;
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.prox-act {
    background: #F0F9FF;
    border-left: 4px solid #00B5B0;
    border-radius: 0 8px 8px 0;
    padding: 10px 16px;
    margin-bottom: 8px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ── Cabecera principal ────────────────────────────────────────
semana_txt = f"Semana {current_week} de 12" if current_week else "Sin fecha de inicio"
inicio_txt = format_date_es(start_date) if start_date else "—"

st.markdown(f"""
<div class="resumen-header">
    <div>
        <div style="font-size:13px;color:rgba(255,255,255,0.6);margin-bottom:4px;">
            COMPLIANCE MONITOR · SCHEDULE · {scenario}
        </div>
        <div style="font-size:26px;font-weight:700;color:white;">
            Resumen Ejecutivo del Proyecto
        </div>
        <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-top:6px;">
            Inicio: {inicio_txt}  ·  {semana_txt}
        </div>
    </div>
    <div style="text-align:right;">
        <div class="resumen-pct">{kpis.pct_completed:.0f}%</div>
        <div style="font-size:13px;color:#00B5B0;font-weight:600;">AVANCE GLOBAL</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Salud ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="salud-box" style="background:{salud_bg};color:{salud_fg};">
    {salud_icon} &nbsp; {salud_label}
</div>
""", unsafe_allow_html=True)

# ── KPIs grandes ─────────────────────────────────────────────
c1, c2, c3 = st.columns(3, gap="medium")
c1.metric("✅ Completadas",  kpis.completed,    f"de {kpis.total}")
c2.metric("🟡 En Progreso",  kpis.in_progress,  "activas")
c3.metric("⚪ Pendientes",   kpis.pending,       "sin iniciar")

st.markdown("---")

col_fases, col_prox = st.columns([1.1, 1], gap="large")

# ── Avance por fase ───────────────────────────────────────────
with col_fases:
    st.subheader("Progreso por Fase")
    for fn, pd_data in phase_progress.items():
        pct = pd_data["pct"]
        bar_color = "#16A34A" if pct >= 80 else ("#D97706" if pct >= 40 else "#003A70")
        emoji     = "✅" if pct == 100 else ("🟡" if pct > 0 else "⚪")
        st.markdown(f"""
        <div class="fase-row">
            <span style="font-size:18px;">{emoji}</span>
            <div style="flex:1;">
                <div style="font-size:13px;font-weight:600;color:#1E293B;">{pd_data['name']}</div>
                <div style="background:#E2E8F0;border-radius:4px;height:8px;margin-top:4px;">
                    <div style="background:{bar_color};width:{pct}%;height:8px;border-radius:4px;"></div>
                </div>
            </div>
            <span style="font-size:15px;font-weight:700;color:{bar_color};">{pct}%</span>
        </div>
        """, unsafe_allow_html=True)

# ── Próximas actividades ──────────────────────────────────────
with col_prox:
    st.subheader("Próximas Actividades a Iniciar")

    pendientes = [a for a in sorted(all_acts, key=lambda x: x.activity_number)
                  if a.status == "PENDIENTE"][:5]

    if not pendientes:
        st.success("🎉 No hay actividades pendientes. ¡El proyecto está completado!")
    else:
        RESP_ICON = {"Desarrollador": "👨‍💻", "TI": "🖥️", "Ambos": "🤝", "Liderazgo": "👔"}
        for act in pendientes:
            rico = RESP_ICON.get(act.responsable, "")
            st.markdown(f"""
            <div class="prox-act">
                <span style="color:#94A3B8;font-size:11px;">#{act.activity_number} · S{act.week_start}–S{act.week_end}</span><br>
                <span style="font-weight:600;color:#1E293B;">{act.activity_name[:60]}</span><br>
                <span style="font-size:12px;color:#64748B;">{rico} {act.responsable}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("💡 Esta vista está diseñada para proyectar en reuniones. Usa el menú lateral para navegar.")
