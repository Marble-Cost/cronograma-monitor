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

import plotly.express as px
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

    **Línea roja punteada** = día de hoy (solo visible si hay fecha de inicio definida)

    **Tip:** Usa los botones del panel superior derecho del gráfico para hacer zoom o descargar la imagen.
    
    Si no hay fecha de inicio definida, ve a ⚙️ Configuración para activar las fechas reales.
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

# Convertir fechas a string para px.timeline
df["start_str"]  = df["start"].astype(str)
df["finish_str"] = df["finish"].astype(str)
df["label_short"] = df.apply(lambda r: f"#{r['activity_number']} {str(r['label']).split(' ',1)[-1][:40]}", axis=1)

# Hover info
df["hover"] = df.apply(lambda r: (
    f"<b>#{r['activity_number']} {str(r['label']).split(' ',1)[-1][:50]}</b><br>"
    f"Fase: {r['fase']}<br>"
    f"Responsable: {r['responsable']}<br>"
    f"Estado: {r['status']}<br>"
    f"Semanas: S{r['week_start']}–S{r['week_end']}<br>"
    + (f"Fechas: {r['start_str']} → {r['finish_str']}" if start_date else "")
), axis=1)

# Paletas de color
COLOR_STATUS = {
    "PENDIENTE":   "#CBD5E1",
    "EN PROGRESO": "#FCD34D",
    "COMPLETADO":  "#4ADE80",
}
COLOR_RESP = {
    "Desarrollador": "#93C5FD",
    "TI":            "#6EE7B7",
    "Ambos":         "#FDE68A",
    "Liderazgo":     "#C4B5FD",
}

color_col = "status" if color_mode == "Estado" else "responsable"
color_map  = COLOR_STATUS if color_mode == "Estado" else COLOR_RESP

fig = px.timeline(
    df.sort_values("activity_number"),
    x_start="start_str",
    x_end="finish_str",
    y="label_short",
    color=color_col,
    color_discrete_map=color_map,
    custom_data=["hover"],
)

fig.update_traces(
    hovertemplate="%{customdata[0]}<extra></extra>",
    marker_line_width=1,
    marker_line_color="rgba(0,0,0,0.15)",
)


# Línea de Hoy
current_week = get_current_week(start_date)
if start_date and current_week:
    today_str = str(date.today())
    fig.add_shape(
        type="line",
        x0=today_str, x1=today_str,
        y0=0, y1=1,
        xref="x", yref="paper",
        line=dict(color="#EF4444", width=2, dash="dash"),
    )
    fig.add_annotation(
        x=today_str, y=1.02,
        xref="x", yref="paper",
        text="Hoy", showarrow=False,
        font=dict(color="#EF4444", size=11, family="DM Sans"),
    )

# Tick marks de semanas en eje X
if start_date:
    tick_dates = [str(start_date + timedelta(weeks=i)) for i in range(13)]
    tick_text  = [f"S{i+1}" for i in range(12)] + ["Fin"]
    fig.update_xaxes(tickvals=tick_dates, ticktext=tick_text,
                     showgrid=True, gridcolor="#F1F5F9",
                     tickfont=dict(size=11, color="#64748B"))
else:
    base_dt    = datetime(2024, 1, 1).date()
    tick_dates = [str(base_dt + timedelta(weeks=i)) for i in range(13)]
    tick_text  = [f"S{i+1}" for i in range(12)] + ["Fin"]
    fig.update_xaxes(tickvals=tick_dates, ticktext=tick_text,
                     showgrid=True, gridcolor="#F1F5F9",
                     tickfont=dict(size=11, color="#64748B"))

fig.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="DM Sans, sans-serif", size=11),
    height=560,
    showlegend=True,
    legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center",
                font=dict(size=11), title_text=""),
    margin=dict(l=10, r=20, t=30, b=50),
    hoverlabel=dict(bgcolor="white", bordercolor="#E2E8F0",
                    font=dict(family="DM Sans", size=12)),
    xaxis_title="",
    yaxis_title="",
    yaxis=dict(
        tickfont=dict(size=10),
        autorange="reversed",
        fixedrange=False,
    ),
    xaxis=dict(fixedrange=False),
    dragmode="pan",
)

st.info("🖱️ **Navega el gráfico:** Haz clic y arrastra para moverte · Usa la rueda del mouse para hacer zoom · Doble clic para restablecer la vista")
st.plotly_chart(fig, use_container_width=True,
    config={"displayModeBar": True, "displaylogo": False, "scrollZoom": True,
            "modeBarButtonsToRemove": ["select2d", "lasso2d"]})

if not start_date:
    st.info("💡 Define la fecha de inicio en ⚙️ Configuración para ver fechas reales y la línea de hoy.")
