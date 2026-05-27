import streamlit as st

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
from app.models import STATUS_COLORS, RESPONSABLE_COLORS, FASES
from app.utils import get_gantt_dataframe, format_date_es, get_current_week

import plotly.graph_objects as go
from datetime import date, timedelta

# ── Auth guard ────────────────────────────────────────────────
require_auth()
inject_global_css()
render_sidebar()

# ── Datos ─────────────────────────────────────────────────────
config     = get_project_config()
scenario   = config.scenario
start_date = config.start_date
activities = get_activities(scenario)

render_page_header(
    "Diagrama Gantt",
    f"Línea de tiempo del proyecto · {scenario} · {'Fechas reales activas' if start_date else 'Configura la fecha inicio en ⚙️ Configuración'}"
)

# ── Filtros compactos ─────────────────────────────────────────
gc1, gc2, gc3 = st.columns([1, 1, 2])
with gc1:
    color_mode = st.radio("Colorear por", ["Estado", "Responsable"], horizontal=True)
with gc2:
    fase_opts = ["Todas"] + [f"FASE {fn}" for fn in range(5)]
    selected_fase = st.selectbox("Fase", fase_opts)
with gc3:
    st.markdown("<br>", unsafe_allow_html=True)

# Filtrar
if selected_fase != "Todas":
    fn_num     = int(selected_fase.split(" ")[1])
    activities = [a for a in activities if a.fase_number == fn_num]

st.markdown("<br>", unsafe_allow_html=True)

if not activities:
    st.info("No hay actividades para mostrar con los filtros seleccionados.")
    st.stop()

# ── Construir Gantt ───────────────────────────────────────────
df = get_gantt_dataframe(activities, start_date)
df_sorted = df.sort_values(["activity_number"], ascending=True)

fig = go.Figure()

# Fondo de fases (franjas alternadas)
fase_groups = df_sorted.groupby("fase")
fase_colors = ["rgba(0,58,112,0.03)", "rgba(0,181,176,0.03)"]
fase_list   = df_sorted["fase"].unique().tolist()

for i, fase_name in enumerate(fase_list):
    fase_rows  = df_sorted[df_sorted["fase"] == fase_name]
    y_vals     = fase_rows["label"].tolist()
    if not y_vals:
        continue
    y_min  = min(df_sorted["label"].tolist().index(y) for y in y_vals)
    y_max  = max(df_sorted["label"].tolist().index(y) for y in y_vals)
    fig.add_hrect(
        y0=y_min - 0.5,
        y1=y_max + 0.5,
        fillcolor=fase_colors[i % 2],
        layer="below",
        line_width=0,
    )

# Barras de actividades
for _, row in df_sorted.iterrows():
    if color_mode == "Estado":
        bar_color = STATUS_COLORS.get(row["status"], "#CBD5E1")
        border_color = {
            "PENDIENTE":   "#94A3B8",
            "EN PROGRESO": "#D97706",
            "COMPLETADO":  "#16A34A",
        }.get(row["status"], "#CBD5E1")
    else:
        bar_color = {
            "Desarrollador": "#93C5FD",
            "TI":            "#86EFAC",
            "Ambos":         "#FCD34D",
            "Liderazgo":     "#C4B5FD",
        }.get(row["responsable"], "#CBD5E1")
        border_color = "#64748B"

    # Duración en días
    duration = (row["finish"] - row["start"]).days

    hover = (
        f"<b>{row['label']}</b><br>"
        f"Fase: {row['fase']}<br>"
        f"Responsable: {row['responsable']}<br>"
        f"Estado: {row['status']}<br>"
        f"Semanas: S{row['week_start']}–S{row['week_end']}<br>"
        f"{'Inicio: ' + row['start'].strftime('%d/%m/%Y') if start_date else ''}"
    )

    fig.add_trace(go.Bar(
        y=[row["label"]],
        x=[duration],
        base=[row["start"]],
        orientation="h",
        marker=dict(
            color=bar_color,
            line=dict(color=border_color, width=1.5),
        ),
        hovertemplate=hover + "<extra></extra>",
        showlegend=False,
        width=0.65,
    ))

# ── Línea de "hoy" si hay fecha inicio ───────────────────────
current_week = get_current_week(start_date)
if start_date and current_week:
    today = date.today()
    fig.add_vline(
        x=today,
        line_color="#EF4444",
        line_dash="dash",
        line_width=2,
        annotation_text="Hoy",
        annotation_position="top",
        annotation_font=dict(color="#EF4444", size=11),
    )

# ── Separadores de fase (líneas horizontales) ─────────────────
y_labels = df_sorted["label"].tolist()
fases_visto = {}
for i, row_data in enumerate(df_sorted.itertuples()):
    if row_data.fase not in fases_visto and i > 0:
        fig.add_hline(y=i - 0.5, line_color="#E2E8F0", line_width=1)
    fases_visto[row_data.fase] = True

# ── Layout del chart ──────────────────────────────────────────
if start_date:
    x_axis = dict(
        type="date",
        tickformat="%d %b",
        showgrid=True,
        gridcolor="#F1F5F9",
        tickfont=dict(size=11, color="#64748B"),
        title="",
    )
    # Ticks por semana
    tick_dates = [start_date + timedelta(weeks=i) for i in range(13)]
    tick_text  = [f"S{i+1}" for i in range(12)] + ["Fin"]
    x_axis["tickvals"] = tick_dates
    x_axis["ticktext"] = tick_text
else:
    from datetime import datetime
    base_dt = datetime(2024, 1, 1).date()
    tick_dates = [base_dt + timedelta(weeks=i) for i in range(13)]
    tick_text  = [f"S{i+1}" for i in range(12)] + ["Fin"]
    x_axis = dict(
        type="date",
        tickvals=tick_dates,
        ticktext=tick_text,
        showgrid=True,
        gridcolor="#F1F5F9",
        tickfont=dict(size=11, color="#64748B"),
        title="",
    )

fig.update_layout(
    barmode="overlay",
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="DM Sans, sans-serif", size=11, color="#374151"),
    height=max(380, len(df_sorted) * 34 + 80),
    xaxis=x_axis,
    yaxis=dict(
        title="",
        tickfont=dict(size=11),
        autorange="reversed",
        showgrid=False,
    ),
    margin=dict(l=10, r=20, t=10, b=30),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#E2E8F0",
        font=dict(family="DM Sans", size=12),
    ),
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})

# ── Leyenda ───────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if color_mode == "Estado":
    st.markdown("""
    <div style="display:flex;gap:20px;align-items:center;flex-wrap:wrap;">
        <span style="font-size:12px;font-weight:600;color:#64748B;">Leyenda (Estado):</span>
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
            <span style="width:14px;height:14px;border-radius:3px;background:#CBD5E1;display:inline-block;"></span>Pendiente
        </span>
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
            <span style="width:14px;height:14px;border-radius:3px;background:#FCD34D;display:inline-block;"></span>En Progreso
        </span>
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
            <span style="width:14px;height:14px;border-radius:3px;background:#4ADE80;display:inline-block;"></span>Completado
        </span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="display:flex;gap:20px;align-items:center;flex-wrap:wrap;">
        <span style="font-size:12px;font-weight:600;color:#64748B;">Leyenda (Responsable):</span>
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
            <span style="width:14px;height:14px;border-radius:3px;background:#93C5FD;display:inline-block;"></span>Desarrollador
        </span>
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
            <span style="width:14px;height:14px;border-radius:3px;background:#86EFAC;display:inline-block;"></span>TI
        </span>
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
            <span style="width:14px;height:14px;border-radius:3px;background:#FCD34D;display:inline-block;"></span>Ambos
        </span>
        <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
            <span style="width:14px;height:14px;border-radius:3px;background:#C4B5FD;display:inline-block;"></span>Liderazgo
        </span>
    </div>
    """, unsafe_allow_html=True)

if not start_date:
    st.markdown("""
    <div class="info-box" style="margin-top:16px;">
        💡 <strong>Tip:</strong> Ve a <strong>⚙️ Configuración</strong> y define la fecha de inicio
        para ver fechas reales en el eje X del Gantt.
    </div>
    """, unsafe_allow_html=True)
