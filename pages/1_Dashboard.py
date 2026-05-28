import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Dashboard · Compliance Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.auth import require_auth
from app.styles import inject_global_css
from app.components import render_sidebar, render_page_header
from app.database import get_kpis, get_phase_progress, get_project_config, get_recent_log
from app.utils import format_date_es, get_current_week, get_end_date, semaforo_fase
import plotly.graph_objects as go

require_auth()
inject_global_css()
render_sidebar()

config         = get_project_config()
start_date     = config.start_date
end_date       = get_end_date(start_date)
current_week   = get_current_week(start_date)

# ── Selector de escenario ─────────────────────────────────────
sc1, sc2 = st.columns([2, 5])
with sc1:
    scenario = st.radio("Escenario", ["Supabase", "SQL Server"],
                        index=0 if config.scenario == "Supabase" else 1,
                        horizontal=True)

kpi            = get_kpis(scenario)
phase_progress = get_phase_progress(scenario)

render_page_header("📊 Dashboard",
    f"Progreso en tiempo real · {scenario} · {format_date_es(start_date)} → {format_date_es(end_date)}")

# ── Indicador de salud del proyecto ──────────────────────────
if start_date and current_week:
    # Calcular progreso esperado vs real
    expected_pct = round((current_week / 12) * 100)
    real_pct     = kpi.pct_completed
    diff         = real_pct - expected_pct

    if real_pct == 100:
        salud_icon, salud_label, salud_color = "🏆", "PROYECTO COMPLETADO", "#16A34A"
    elif diff >= 0:
        salud_icon, salud_label, salud_color = "🟢", "EN TIEMPO", "#16A34A"
    elif diff >= -15:
        salud_icon, salud_label, salud_color = "🟡", "LIGERAMENTE ATRASADO", "#D97706"
    else:
        salud_icon, salud_label, salud_color = "🔴", "EN RIESGO", "#DC2626"

    weeks_left = 12 - current_week
    st.markdown(f"""
    <div style="background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:12px;
                padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;
                justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div>
            <span style="font-size:20px;">{salud_icon}</span>
            <span style="font-size:15px;font-weight:700;color:{salud_color};margin-left:8px;">{salud_label}</span>
            <span style="font-size:13px;color:#64748B;margin-left:12px;">
                Semana {current_week} de 12 · {weeks_left} semana(s) restante(s)
            </span>
        </div>
        <div style="font-size:13px;color:#64748B;">
            Avance esperado: <strong>{expected_pct}%</strong> · 
            Avance real: <strong style="color:{salud_color};">{real_pct:.0f}%</strong> · 
            Diferencia: <strong style="color:{salud_color};">{'+' if diff>=0 else ''}{diff:.0f}%</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Actividades atrasadas
    all_acts = __import__('app.database', fromlist=['get_activities']).get_activities(scenario)
    atrasadas = [a for a in all_acts
                 if a.status == "PENDIENTE" and a.week_start <= current_week]
    if atrasadas:
        with st.expander(f"⚠️ {len(atrasadas)} actividad(es) deberían haber iniciado ya", expanded=True):
            for a in atrasadas:
                st.markdown(f"- **#{a.activity_number}** {a.activity_name} · _{a.responsable}_ · debió iniciar en S{a.week_start}")

elif not start_date:
    st.info("💡 Define la **fecha de inicio** en ⚙️ Configuración para activar el indicador de salud del proyecto.")

# ── KPIs ──────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3, c4 = st.columns(4, gap="medium")
c1.metric("⚪ Pendientes",    kpi.pending,      "actividades sin iniciar")
c2.metric("🟡 En Progreso",   kpi.in_progress,  "actividades activas")
c3.metric("✅ Completadas",   kpi.completed,    "actividades finalizadas")
c4.metric("📈 % Completado",  f"{kpi.pct_completed:.0f}%", f"de {kpi.total} totales")

st.markdown("---")

# ── Avance por fase ───────────────────────────────────────────
st.subheader("Avance por Fase")
for fn, pd_data in phase_progress.items():
    emoji, label = semaforo_fase(pd_data)
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2], gap="small")
    col1.markdown(f"**{pd_data['name']}**")
    col2.markdown(f"{emoji} {label}")
    col3.markdown(f"✅ {pd_data['completed']}")
    col4.markdown(f"🟡 {pd_data['in_progress']}")
    col5.progress(pd_data['pct'] / 100, text=f"{pd_data['pct']}%")

st.markdown("---")

# ── Gráficos ──────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns([1, 1.4], gap="large")

with chart_col1:
    st.subheader("Avance General")
    fig_donut = go.Figure(data=[go.Pie(
        labels=["Completado", "En Progreso", "Pendiente"],
        values=[kpi.completed, kpi.in_progress, kpi.pending],
        hole=0.65, marker_colors=["#22C55E", "#FCD34D", "#E2E8F0"],
        textinfo="none", hovertemplate="%{label}: %{value}<extra></extra>",
    )])
    fig_donut.add_annotation(text=f"<b>{kpi.pct_completed:.0f}%</b>",
        font=dict(size=30, color="#003A70"), showarrow=False, x=0.5, y=0.52)
    fig_donut.add_annotation(text="completado",
        font=dict(size=12, color="#64748B"), showarrow=False, x=0.5, y=0.38)
    fig_donut.update_layout(paper_bgcolor="white", plot_bgcolor="white", showlegend=True,
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
        margin=dict(t=10, b=10, l=10, r=10), height=250)
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

with chart_col2:
    st.subheader("Actividades por Fase")
    fase_names  = [f"F{fn}" for fn in phase_progress.keys()]
    hover_names = [ph["name"] for ph in phase_progress.values()]
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="Completadas", x=fase_names,
        y=[ph["completed"] for ph in phase_progress.values()], marker_color="#22C55E",
        customdata=hover_names, hovertemplate="%{customdata}<br>Completadas: %{y}<extra></extra>"))
    fig_bar.add_trace(go.Bar(name="En Progreso", x=fase_names,
        y=[ph["in_progress"] for ph in phase_progress.values()], marker_color="#FCD34D",
        customdata=hover_names, hovertemplate="%{customdata}<br>En Progreso: %{y}<extra></extra>"))
    fig_bar.add_trace(go.Bar(name="Pendientes", x=fase_names,
        y=[ph["pending"] for ph in phase_progress.values()], marker_color="#E2E8F0",
        customdata=hover_names, hovertemplate="%{customdata}<br>Pendientes: %{y}<extra></extra>"))
    fig_bar.update_layout(barmode="stack", paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center"),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        margin=dict(t=10, b=10, l=0, r=0), height=250)
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")

# ── Últimas novedades ─────────────────────────────────────────
st.subheader("📰 Últimas novedades del proyecto")
st.caption("Los cambios más recientes registrados por cualquier usuario del sistema.")
logs = get_recent_log(8)
if not logs:
    st.info("Aún no hay cambios registrados. Los cambios aparecerán aquí cuando el admin actualice actividades.")
else:
    for log in logs:
        act_name   = "—"
        if log.get("activities"):
            act_name = log["activities"].get("activity_name", "—")[:55]
        changed_at = log.get("changed_at", "")[:16].replace("T", " ")
        user_email = log.get("user_email", "—")
        old_s      = log.get("old_status", "—")
        new_s      = log.get("new_status", "—")
        obs        = log.get("observation", "")
        icon_new   = {"PENDIENTE": "⚪", "EN PROGRESO": "🟡", "COMPLETADO": "✅"}.get(new_s, "•")

        obs_html = f"<br><span style='font-style:italic;color:#64748B;'>💬 {obs[:80]}</span>" if obs else ""
        st.markdown(f"""
        <div style="padding:10px 0;border-bottom:1px solid #F1F5F9;">
            <span style="font-size:11px;color:#94A3B8;">{changed_at}</span>
            <span style="font-size:13px;font-weight:600;color:#1E293B;margin:0 8px;">{icon_new} {act_name}</span>
            <span style="font-size:11px;color:#64748B;">{old_s} → <strong>{new_s}</strong> · {user_email}</span>
            {obs_html}
        </div>
        """, unsafe_allow_html=True)
