import streamlit as st
from datetime import date, timedelta

st.set_page_config(
    page_title="Gantt · Compliance Monitor",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.auth import require_auth
from app.styles import inject_global_css
from app.components import render_sidebar, render_page_header
from app.database import get_activities, get_project_config
from app.models import STATUS_COLORS
from app.utils import get_gantt_dataframe, format_date_es, get_current_week

import plotly.graph_objects as go

require_auth()
inject_global_css()
render_sidebar()

config     = get_project_config()
scenario   = config.scenario
start_date = config.start_date
activities = get_activities(scenario)

render_page_header("📅 Diagrama Gantt", f"Línea de tiempo · {scenario} · {'Fechas reales activas' if start_date else 'Sin fecha de inicio definida'}")

# ── Guía ──────────────────────────────────────────────────────
with st.expander("📖 Guía de uso — ¿Cómo leer el Gantt?", expanded=False):
    st.markdown("""
    **El diagrama de Gantt muestra la línea de tiempo del proyecto.**
    
    **Cómo leer las barras:**
    - Cada barra representa una actividad. Su longitud indica cuántas semanas dura.
    - El color indica el estado actual de la actividad.
    - La **línea roja vertical** marca el día de hoy (solo aparece si hay fecha de inicio definida).
    - Pasa el cursor sobre cualquier barra para ver los detalles completos.
    
    **Colores:**
    - ⬜ **Gris** → PENDIENTE (no iniciada)
    - 🟨 **Amarillo** → EN PROGRESO (en ejecución)
    - 🟩 **Verde** → COMPLETADO (finalizada)
    - 🟦 **Azul** → Al colorear por responsable: Desarrollador
    - 🟩 **Verde agua** → TI
    - 🟨 **Amarillo** → Ambos
    - 🟪 **Morado** → Liderazgo
    
    **Filtros:** Usa los selectores arriba para enfocarte en una fase o responsable específico.
    
    **Sin fecha de inicio:** Si las semanas muestran "S1, S2..." en vez de fechas reales, ve a ⚙️ Configuración y define la fecha de inicio del proyecto.
    """)

st.markdown("---")

# ── Filtros ───────────────────────────────────────────────────
gc1, gc2, gc3 = st.columns([1, 1, 1], gap="medium")
with gc1:
    color_mode = st.radio("Colorear por", ["Estado", "Responsable"], horizontal=True)
with gc2:
    fase_opts    = ["Todas las fases"] + [f"FASE {fn}" for fn in range(5)]
    sel_fase     = st.selectbox("Fase", fase_opts)
with gc3:
    from app.models import RESPONSABLES
    resp_opts = ["Todos"] + RESPONSABLES
    sel_resp  = st.selectbox("Responsable", resp_opts)

# Filtrar
filtered = activities
if sel_fase != "Todas las fases":
    fn_num   = int(sel_fase.split(" ")[1])
    filtered = [a for a in filtered if a.fase_number == fn_num]
if sel_resp != "Todos":
    filtered = [a for a in filtered if a.responsable == sel_resp]

if not filtered:
    st.info("No hay actividades para mostrar con los filtros seleccionados.")
    st.stop()

# ── Construir Gantt ───────────────────────────────────────────
df = get_gantt_dataframe(filtered, start_date)

COLORS_STATUS = {
    "PENDIENTE":   "#CBD5E1",
    "EN PROGRESO": "#FCD34D",
    "COMPLETADO":  "#4ADE80",
}
COLORS_RESP = {
    "Desarrollador": "#93C5FD",
    "TI":            "#6EE7B7",
    "Ambos":         "#FDE68A",
    "Liderazgo":     "#C4B5FD",
}
BORDER_STATUS = {
    "PENDIENTE":   "#94A3B8",
    "EN PROGRESO": "#D97706",
    "COMPLETADO":  "#16A34A",
}

fig = go.Figure()

for _, row in df.sort_values("activity_number").iterrows():
    bar_color    = COLORS_STATUS[row["status"]] if color_mode == "Estado" else COLORS_RESP.get(row["responsable"], "#CBD5E1")
    border_color = BORDER_STATUS.get(row["status"], "#94A3B8")
    duration     = (row["finish"] - row["start"]).days

    hover = (
        f"<b>#{row['activity_number']} {row['label'].split(' ', 1)[-1][:50]}</b><br>"
        f"<b>Fase:</b> {row['fase']}<br>"
        f"<b>Responsable:</b> {row['responsable']}<br>"
        f"<b>Estado:</b> {row['status']}<br>"
        f"<b>Semanas:</b> S{row['week_start']}–S{row['week_end']}"
    )
    if start_date:
        hover += f"<br><b>Fechas:</b> {row['start'].strftime('%d/%m/%Y')} → {row['finish'].strftime('%d/%m/%Y')}"

    fig.add_trace(go.Bar(
        y=[f"#{row['activity_number']} {row['label'].split(' ',1)[-1][:40]}"],
        x=[duration],
        base=[row["start"]],
        orientation="h",
        marker=dict(color=bar_color, line=dict(color=border_color, width=1.5)),
        hovertemplate=hover + "<extra></extra>",
        showlegend=False,
        width=0.6,
    ))

# Línea de hoy
current_week = get_current_week(start_date)
if start_date and current_week:
    fig.add_vline(
        x=date.today(),
        line_color="#EF4444", line_dash="dash", line_width=2,
        annotation_text="Hoy",
        annotation_font=dict(color="#EF4444", size=11),
    )

# Eje X
if start_date:
    tick_dates = [start_date + timedelta(weeks=i) for i in range(13)]
    tick_text  = [f"S{i+1}" for i in range(12)] + ["Fin"]
    x_axis = dict(type="date", tickvals=tick_dates, ticktext=tick_text,
                  showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=11, color="#64748B"))
else:
    from datetime import datetime
    base_dt    = datetime(2024, 1, 1).date()
    tick_dates = [base_dt + timedelta(weeks=i) for i in range(13)]
    tick_text  = [f"S{i+1}" for i in range(12)] + ["Fin"]
    x_axis = dict(type="date", tickvals=tick_dates, ticktext=tick_text,
                  showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=11, color="#64748B"))

fig.update_layout(
    barmode="overlay",
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="DM Sans, sans-serif", size=11),
    height=max(400, len(df) * 36 + 80),
    xaxis=x_axis,
    yaxis=dict(title="", tickfont=dict(size=10), autorange="reversed", showgrid=False),
    margin=dict(l=10, r=20, t=20, b=30),
    hoverlabel=dict(bgcolor="white", bordercolor="#E2E8F0", font=dict(family="DM Sans", size=12)),
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})

# ── Leyenda ───────────────────────────────────────────────────
st.markdown("---")
if color_mode == "Estado":
    col1, col2, col3 = st.columns(3)
    col1.markdown("⬜ **Gris** — PENDIENTE")
    col2.markdown("🟨 **Amarillo** — EN PROGRESO")
    col3.markdown("🟩 **Verde** — COMPLETADO")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown("🟦 **Azul** — Desarrollador")
    col2.markdown("🟩 **Verde** — TI")
    col3.markdown("🟨 **Amarillo** — Ambos")
    col4.markdown("🟪 **Morado** — Liderazgo")

if not start_date:
    st.info("💡 Define la fecha de inicio en ⚙️ Configuración para ver fechas reales en el eje X.")
