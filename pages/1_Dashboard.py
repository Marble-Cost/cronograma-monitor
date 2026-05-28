import streamlit as st

st.set_page_config(
    page_title="Dashboard · Compliance Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.auth import require_auth
from app.styles import inject_global_css
from app.components import render_sidebar, kpi_card, progress_bar_html, render_page_header
from app.database import get_kpis, get_phase_progress, get_project_config
from app.utils import format_date_es, get_current_week, get_end_date, semaforo_fase

import plotly.graph_objects as go

require_auth()
inject_global_css()
render_sidebar()

config        = get_project_config()
scenario      = config.scenario
start_date    = config.start_date
end_date      = get_end_date(start_date)
current_week  = get_current_week(start_date)
kpi           = get_kpis(scenario)
phase_progress = get_phase_progress(scenario)

render_page_header(
    "Dashboard",
    f"Progreso en tiempo real · Escenario: {scenario} · {format_date_es(start_date)} → {format_date_es(end_date)}"
)

if current_week:
    st.markdown(
        f'<span style="background:#EFF6FF;color:#1D4ED8;border-radius:20px;'
        f'padding:4px 14px;font-size:12px;font-weight:600;">📍 Semana actual: S{current_week} de 12</span>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1:
    st.markdown(kpi_card(kpi.pending, "Pendientes", "actividades sin iniciar", "kpi-gray", "⚪"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card(kpi.in_progress, "En Progreso", "actividades activas", "kpi-warning", "🟡"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card(kpi.completed, "Completadas", "actividades finalizadas", "kpi-success", "✅"), unsafe_allow_html=True)
with c4:
    pct_display = f"{kpi.pct_completed:.0f}%"
    st.markdown(kpi_card(pct_display, "% Completado", f"de {kpi.total} actividades totales", "kpi-teal", "📈"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Avance por Fase ───────────────────────────────────────────
st.markdown('<div class="section-title">Avance por Fase</div>', unsafe_allow_html=True)

phase_table_html = """
<table class="phase-table">
<thead>
<tr>
    <th>Fase</th>
    <th>Semáforo</th>
    <th>Completadas</th>
    <th>En progreso</th>
    <th>Pendientes</th>
    <th style="min-width:200px;">Progreso</th>
</tr>
</thead>
<tbody>
"""

for fn, pd_data in phase_progress.items():
    done = pd_data["pct"] == 100
    emoji, label = semaforo_fase(pd_data)
    bar = progress_bar_html(pd_data["pct"], done=done)
    phase_table_html += f"""
    <tr>
        <td class="fase-name">{pd_data['name']}</td>
        <td>{emoji} {label}</td>
        <td style="text-align:center;font-weight:600;color:#16A34A;">{pd_data['completed']}</td>
        <td style="text-align:center;font-weight:600;color:#D97706;">{pd_data['in_progress']}</td>
        <td style="text-align:center;color:#64748B;">{pd_data['pending']}</td>
        <td>{bar}</td>
    </tr>
    """

phase_table_html += "</tbody></table>"
st.markdown(phase_table_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns([1, 1.4], gap="large")

with chart_col1:
    st.markdown('<div class="section-title">Avance General</div>', unsafe_allow_html=True)
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
        font=dict(size=32, color="#003A70", family="DM Sans"),
        showarrow=False, x=0.5, y=0.52,
    )
    fig_donut.add_annotation(
        text="completado",
        font=dict(size=13, color="#64748B", family="DM Sans"),
        showarrow=False, x=0.5, y=0.38,
    )
    fig_donut.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=True,
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(size=12)),
        margin=dict(t=10, b=10, l=10, r=10), height=260,
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

with chart_col2:
    st.markdown('<div class="section-title">Actividades por Fase</div>', unsafe_allow_html=True)
    fase_names  = [f"F{fn}" for fn in phase_progress.keys()]
    completadas = [ph["completed"]   for ph in phase_progress.values()]
    en_prog     = [ph["in_progress"] for ph in phase_progress.values()]
    pendientes  = [ph["pending"]     for ph in phase_progress.values()]
    hover_names = [ph["name"][:30]   for ph in phase_progress.values()]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="Completadas", x=fase_names, y=completadas, marker_color="#22C55E",
                             customdata=hover_names, hovertemplate="%{customdata}<br>Completadas: %{y}<extra></extra>"))
    fig_bar.add_trace(go.Bar(name="En Progreso", x=fase_names, y=en_prog,     marker_color="#FCD34D",
                             customdata=hover_names, hovertemplate="%{customdata}<br>En Progreso: %{y}<extra></extra>"))
    fig_bar.add_trace(go.Bar(name="Pendientes",  x=fase_names, y=pendientes,  marker_color="#E2E8F0",
                             customdata=hover_names, hovertemplate="%{customdata}<br>Pendientes: %{y}<extra></extra>"))
    fig_bar.update_layout(
        barmode="stack", paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#374151"),
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center", font=dict(size=11)),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        margin=dict(t=10, b=10, l=0, r=0), height=260,
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
