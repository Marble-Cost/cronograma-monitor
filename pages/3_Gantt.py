import streamlit as st
from datetime import date, timedelta, datetime

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
from app.models import RESPONSABLES
from app.utils import get_gantt_dataframe, get_current_week

import plotly.graph_objects as go

require_auth()
inject_global_css()
render_sidebar()

config     = get_project_config()
start_date = config.start_date

render_page_header("📅 Diagrama Gantt", "Línea de tiempo del proyecto · Pasa el cursor sobre una barra para ver el detalle")

with st.expander("📖 Guía de lectura", expanded=False):
    st.markdown("""
    **Las barras** representan actividades. Su longitud indica la duración en semanas.

    **Colores por estado:** ⬜ Gris = PENDIENTE · 🟨 Amarillo = EN PROGRESO · 🟩 Verde = COMPLETADO

    **Colores por responsable:** 🟦 Azul = Desarrollador · 🟩 Verde = TI · 🟨 Amarillo = Ambos · 🟪 Morado = Liderazgo

    **Línea roja punteada** = día de hoy (solo visible si hay fecha de inicio definida en ⚙️ Configuración)

    **Interactividad:** Pasa el cursor sobre cualquier barra para ver nombre, fase, responsable, estado y fechas exactas.
    Usa los botones del panel del gráfico para hacer zoom o descargar la imagen.
    """)

st.markdown("---")

gc1, gc2, gc3, gc4 = st.columns([1, 1, 1, 1], gap="medium")
with gc1:
    scenario = st.radio("Escenario", ["Supabase", "SQL Server"],
                        index=0 if config.scenario == "Supabase" else 1, horizontal=True)
with gc2:
    color_mode = st.radio("Colorear por", ["Estado", "Responsable"], horizontal=True)
with gc3:
    fase_opts = ["Todas las fases"] + [f"FASE {fn}" for fn in range(5)]
    sel_fase  = st.selectbox("Fase", fase_opts)
with gc4:
    resp_opts = ["Todos"] + RESPONSABLES
    sel_resp  = st.selectbox("Responsable", resp_opts)

activities = get_activities(scenario)
if sel_fase != "Todas las fases":
    fn_num     = int(sel_fase.split(" ")[1])
    activities = [a for a in activities if a.fase_number == fn_num]
if sel_resp != "Todos":
    activities = [a for a in activities if a.responsable == sel_resp]

if not activities:
    st.info("No hay actividades para los filtros seleccionados.")
    st.stop()

df = get_gantt_dataframe(activities, start_date)

COLORS_STATUS = {"PENDIENTE": "#CBD5E1", "EN PROGRESO": "#FCD34D", "COMPLETADO": "#4ADE80"}
BORDER_STATUS = {"PENDIENTE": "#94A3B8", "EN PROGRESO": "#D97706", "COMPLETADO": "#16A34A"}
COLORS_RESP   = {"Desarrollador": "#93C5FD", "TI": "#6EE7B7", "Ambos": "#FDE68A", "Liderazgo": "#C4B5FD"}

fig = go.Figure()

for _, row in df.sort_values("activity_number").iterrows():
    bar_color    = COLORS_STATUS[row["status"]] if color_mode == "Estado" else COLORS_RESP.get(row["responsable"], "#CBD5E1")
    border_color = BORDER_STATUS.get(row["status"], "#94A3B8")
    duration     = (row["finish"] - row["start"]).days

    hover = (
        f"<b>#{row['activity_number']} {str(row['label']).split(' ',1)[-1][:50]}</b><br>"
        f"<b>Fase:</b> {row['fase']}<br>"
        f"<b>Responsable:</b> {row['responsable']}<br>"
        f"<b>Estado:</b> {row['status']}<br>"
        f"<b>Semanas:</b> S{row['week_start']}–S{row['week_end']}"
    )
    if start_date:
        hover += f"<br><b>Fechas:</b> {row['start'].strftime('%d/%m/%Y')} → {row['finish'].strftime('%d/%m/%Y')}"

    fig.add_trace(go.Bar(
        y=[f"#{row['activity_number']} {str(row['label']).split(' ',1)[-1][:38]}"],
        x=[duration], base=[row["start"]], orientation="h",
        marker=dict(color=bar_color, line=dict(color=border_color, width=1.5)),
        hovertemplate=hover + "<extra></extra>",
        showlegend=False, width=0.6,
    ))

current_week = get_current_week(start_date)
if start_date and current_week:
    fig.add_vline(x=date.today(), line_color="#EF4444", line_dash="dash", line_width=2,
                  annotation_text="Hoy", annotation_font=dict(color="#EF4444", size=11))

if start_date:
    tick_dates = [start_date + timedelta(weeks=i) for i in range(13)]
    tick_text  = [f"S{i+1}" for i in range(12)] + ["Fin"]
else:
    base_dt    = datetime(2024, 1, 1).date()
    tick_dates = [base_dt + timedelta(weeks=i) for i in range(13)]
    tick_text  = [f"S{i+1}" for i in range(12)] + ["Fin"]

fig.update_layout(
    barmode="overlay", paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="DM Sans, sans-serif", size=11),
    height=max(400, len(df) * 36 + 80),
    xaxis=dict(type="date", tickvals=tick_dates, ticktext=tick_text,
               showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=11, color="#64748B")),
    yaxis=dict(title="", tickfont=dict(size=10), autorange="reversed", showgrid=False),
    margin=dict(l=10, r=20, t=20, b=30),
    hoverlabel=dict(bgcolor="white", bordercolor="#E2E8F0", font=dict(family="DM Sans", size=12)),
)

st.plotly_chart(fig, use_container_width=True,
    config={"displayModeBar": True, "displaylogo": False,
            "modeBarButtonsToRemove": ["select2d", "lasso2d"]})

st.markdown("---")
if color_mode == "Estado":
    c1, c2, c3 = st.columns(3)
    c1.markdown("⬜ **Gris** — PENDIENTE")
    c2.markdown("🟨 **Amarillo** — EN PROGRESO")
    c3.markdown("🟩 **Verde** — COMPLETADO")
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("🟦 **Azul** — Desarrollador")
    c2.markdown("🟩 **Verde agua** — TI")
    c3.markdown("🟨 **Amarillo** — Ambos")
    c4.markdown("🟪 **Morado** — Liderazgo")

if not start_date:
    st.info("💡 Define la fecha de inicio en ⚙️ Configuración para ver fechas reales y la línea de hoy.")
