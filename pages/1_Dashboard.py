import streamlit as st

st.set_page_config(
    page_title="Dashboard · Compliance Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.auth import require_auth
from app.styles import inject_global_css
from app.components import render_sidebar, render_page_header
from app.database import get_kpis, get_phase_progress, get_project_config
from app.utils import format_date_es, get_current_week, get_end_date, semaforo_fase
import plotly.graph_objects as go

require_auth()
inject_global_css()
render_sidebar()

config         = get_project_config()
scenario       = config.scenario
start_date     = config.start_date
end_date       = get_end_date(start_date)
current_week   = get_current_week(start_date)
kpi            = get_kpis(scenario)
phase_progress = get_phase_progress(scenario)

render_page_header(
    "Dashboard",
    f"Progreso en tiempo real · {scenario} · {format_date_es(start_date)} → {format_date_es(end_date)}"
)

if current_week:
    st.info(f"📍 Semana actual: S{current_week} de 12")

st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4, gap="medium")
c1.metric("⚪ Pendientes",   kpi.pending,      "actividades sin iniciar")
c2.metric("🟡 En Progreso",  kpi.in_progress,  "actividades activas")
c3.metric("✅ Completadas",  kpi.completed,    "actividades finalizadas")
c4.metric("📈 % Completado", f"{kpi.pct_completed:.0f}%", f"de {kpi.total} totales")

st.markdown("---")

# ── Avance por Fase ───────────────────────────────────────────
st.subheader("Avance por Fase")

for fn, pd_data in phase_progress.items():
    emoji, label = semaforo_fase(pd_data)
    pct          = pd_data["pct"]
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2], gap="small")

    col1.markdown(f"**{pd_data['name']}**")
    col2.markdown(f"{emoji} {label}")
    col3.markdown(f"✅ {pd_data['completed']}")
    col4.markdown(f"🟡 {pd_data['in_progress']}")
    col5.progress(pct / 100, text=f"{pct}%")

st.markdown("---")

# ── Charts ────────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns([1, 1.4], gap="large")

with chart_col1:
    st.subheader("Avance General")
    fig_donut = go.Figure(data=[go.Pie(
        labels=["Completado", "En Progreso", "Pendiente"],
        values=[kpi.completed, kpi.in_progress, kpi.pending],
        hole=0.65,
        marker_colors=["#22C55E", "#FCD34D", "#E2E8F0"],
        textinfo="none",
        hovertemplate="%{label}: %{value} actividades<extra></extra>",
    )])
    fig_donut.add_annotation(
        text=f"<b>{kpi.pct_completed:.0f}%</b>",
        font=dict(size=32, color="#003A70"), showarrow=False, x=0.5, y=0.52,
    )
    fig_donut.add_annotation(
        text="completado",
        font=dict(size=13, color="#64748B"), showarrow=False, x=0.5, y=0.38,
    )
    fig_donut.update_layout(
        paper_bgcolor="white", plot_bgcolor="white", showlegend=True,
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
        margin=dict(t=10, b=10, l=10, r=10), height=260,
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

with chart_col2:
    st.subheader("Actividades por Fase")
    fase_names  = [f"F{fn}" for fn in phase_progress.keys()]
    completadas = [ph["completed"]   for ph in phase_progress.values()]
    en_prog     = [ph["in_progress"] for ph in phase_progress.values()]
    pendientes  = [ph["pending"]     for ph in phase_progress.values()]
    hover_names = [ph["name"]        for ph in phase_progress.values()]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="Completadas", x=fase_names, y=completadas,
                             marker_color="#22C55E", customdata=hover_names,
                             hovertemplate="%{customdata}<br>Completadas: %{y}<extra></extra>"))
    fig_bar.add_trace(go.Bar(name="En Progreso", x=fase_names, y=en_prog,
                             marker_color="#FCD34D", customdata=hover_names,
                             hovertemplate="%{customdata}<br>En Progreso: %{y}<extra></extra>"))
    fig_bar.add_trace(go.Bar(name="Pendientes",  x=fase_names, y=pendientes,
                             marker_color="#E2E8F0", customdata=hover_names,
                             hovertemplate="%{customdata}<br>Pendientes: %{y}<extra></extra>"))
    fig_bar.update_layout(
        barmode="stack", paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center"),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        margin=dict(t=10, b=10, l=0, r=0), height=260,
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
