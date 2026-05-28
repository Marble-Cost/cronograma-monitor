import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Cronograma · Compliance Monitor",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.auth import require_auth, is_admin
from app.styles import inject_global_css
from app.components import render_sidebar, render_page_header, render_no_permission_warning
from app.database import get_activities, get_project_config, update_activity_status
from app.models import STATUSES, RESPONSABLES

require_auth()
inject_global_css()
render_sidebar()

# ── Helper: última observación de una actividad ───────────────
def get_last_obs(activity_id: int) -> str:
    try:
        from app.auth import get_supabase_client
        client = get_supabase_client()
        res = (client.table("activity_log")
               .select("observation")
               .eq("activity_id", activity_id)
               .not_.is_("observation", "null")
               .order("changed_at", desc=True)
               .limit(1).execute())
        if res.data:
            return res.data[0].get("observation", "") or ""
    except Exception:
        pass
    return ""

# ── Datos ─────────────────────────────────────────────────────
config   = get_project_config()
scenario = config.scenario

render_page_header("📋 Cronograma", f"Gestión de actividades · Escenario: {scenario}")

# ── Guía ──────────────────────────────────────────────────────
with st.expander("📖 Guía de uso — ¿Cómo funciona esta sección?", expanded=False):
    st.markdown("""
    **Esta sección es el centro de control del proyecto.**

    **Estados de actividad:**
    - ⚪ **PENDIENTE** — La actividad aún no ha comenzado
    - 🟡 **EN PROGRESO** — La actividad está siendo ejecutada actualmente
    - ✅ **COMPLETADO** — La actividad fue finalizada exitosamente

    **Cómo actualizar una actividad:**
    1. Localiza la actividad en la tabla (usa los filtros si hay muchas)
    2. Haz clic en el botón de acción:
       - **▶ Iniciar** → cambia de PENDIENTE a EN PROGRESO
       - **✅ Completar** → cambia de EN PROGRESO a COMPLETADO
       - **↩ Reabrir** → devuelve a EN PROGRESO si fue completada por error
    3. Se abrirá un panel para dejar una observación (recomendado)
    4. Confirma — quedará guardado permanentemente

    **Responsables:**
    - 👨‍💻 **Desarrollador** — Tareas técnicas de implementación
    - 🖥️ **TI** — Infraestructura y servidores
    - 🤝 **Ambos** — Coordinación entre Desarrollador y TI
    - 👔 **Liderazgo** — Aprobaciones y decisiones estratégicas
    """)

st.markdown("---")

# ── Filtros ───────────────────────────────────────────────────
fc1, fc2, fc3, fc4 = st.columns(4, gap="medium")
with fc1:
    fase_opts = ["Todas las fases", "FASE 0", "FASE 1", "FASE 2", "FASE 3", "FASE 4"]
    sel_fase  = st.selectbox("Filtrar por fase", fase_opts)
with fc2:
    resp_opts = ["Todos"] + RESPONSABLES
    sel_resp  = st.selectbox("Filtrar por responsable", resp_opts)
with fc3:
    stat_opts = ["Todos"] + STATUSES
    sel_stat  = st.selectbox("Filtrar por estado", stat_opts)
with fc4:
    buscar = st.text_input("Buscar actividad", placeholder="Escribe para buscar...")

# ── Carga y filtrado ──────────────────────────────────────────
activities = get_activities(scenario)

if sel_fase != "Todas las fases":
    fn = int(sel_fase.split(" ")[1])
    activities = [a for a in activities if a.fase_number == fn]
if sel_resp != "Todos":
    activities = [a for a in activities if a.responsable == sel_resp]
if sel_stat != "Todos":
    activities = [a for a in activities if a.status == sel_stat]
if buscar:
    activities = [a for a in activities if buscar.lower() in a.activity_name.lower()]

n_pend = sum(1 for a in activities if a.status == "PENDIENTE")
n_prog = sum(1 for a in activities if a.status == "EN PROGRESO")
n_done = sum(1 for a in activities if a.status == "COMPLETADO")

st.markdown(f"**{len(activities)} actividades** · ⚪ {n_pend} pendientes · 🟡 {n_prog} en progreso · ✅ {n_done} completadas")
st.markdown("---")

if not activities:
    st.info("No hay actividades que coincidan con los filtros.")
    st.stop()

# ── Estado de acción pendiente ────────────────────────────────
if "accion_pendiente" not in st.session_state:
    st.session_state.accion_pendiente = None

# ── Panel de confirmación ─────────────────────────────────────
if st.session_state.accion_pendiente:
    ap = st.session_state.accion_pendiente
    nuevo_estado = {"iniciar": "EN PROGRESO", "completar": "COMPLETADO", "reabrir": "EN PROGRESO"}[ap["accion"]]
    icono        = {"iniciar": "▶", "completar": "✅", "reabrir": "↩"}[ap["accion"]]

    st.info(f"{icono} **Confirmando acción** — #{ap['numero']} {ap['nombre'][:60]}  \n"
            f"Estado actual: **{ap['estado_actual']}** → Nuevo estado: **{nuevo_estado}**")

    obs = st.text_area(
        "📝 Observación (recomendado — queda guardada en el historial)",
        placeholder="Describe qué ocurrió, qué se entregó, o por qué se realiza este cambio...",
        height=90, key="obs_input"
    )

    cc1, cc2, _ = st.columns([1, 1, 3])
    with cc1:
        if st.button("✅ Confirmar cambio", type="primary", use_container_width=True):
            ok = update_activity_status(ap["id"], nuevo_estado, ap["estado_actual"], obs.strip() or None)
            if ok:
                st.success(f"Actividad actualizada a **{nuevo_estado}**")
                st.session_state.accion_pendiente = None
                st.rerun()
    with cc2:
        if st.button("✗ Cancelar", use_container_width=True):
            st.session_state.accion_pendiente = None
            st.rerun()

    st.markdown("---")

# ── Tabla por fases ───────────────────────────────────────────
STATUS_ICON = {"PENDIENTE": "⚪", "EN PROGRESO": "🟡", "COMPLETADO": "✅"}
RESP_ICON   = {"Desarrollador": "👨‍💻", "TI": "🖥️", "Ambos": "🤝", "Liderazgo": "👔"}

for fase_num in sorted(set(a.fase_number for a in activities)):
    fase_acts = [a for a in activities if a.fase_number == fase_num]
    if not fase_acts:
        continue

    fase_name       = fase_acts[0].fase_name
    completadas_fase = sum(1 for a in fase_acts if a.status == "COMPLETADO")
    pct_fase        = int(completadas_fase / len(fase_acts) * 100)

    st.markdown(f"#### {fase_name} · {pct_fase}% completada")
    st.progress(pct_fase / 100)

    for act in fase_acts:
        icon  = STATUS_ICON.get(act.status, "⚪")
        rico  = RESP_ICON.get(act.responsable, "")
        color = {"PENDIENTE": "#94A3B8", "EN PROGRESO": "#D97706", "COMPLETADO": "#16A34A"}.get(act.status, "#94A3B8")

        c_num, c_name, c_resp, c_weeks, c_status, c_obs, c_btn = st.columns(
            [0.5, 3.5, 1.2, 0.8, 1.3, 2.5, 1.3], gap="small"
        )

        c_num.markdown(f"<div style='padding-top:8px;color:#94A3B8;font-size:12px;'>#{act.activity_number}</div>", unsafe_allow_html=True)
        c_name.markdown(f"<div style='padding-top:8px;font-size:13px;font-weight:500;'>{act.activity_name}</div>", unsafe_allow_html=True)
        c_resp.markdown(f"<div style='padding-top:8px;font-size:12px;color:#475569;'>{rico} {act.responsable}</div>", unsafe_allow_html=True)
        c_weeks.markdown(f"<div style='padding-top:8px;font-size:12px;color:#64748B;'>S{act.week_start}–S{act.week_end}</div>", unsafe_allow_html=True)
        c_status.markdown(f"<div style='padding-top:8px;font-size:12px;font-weight:600;color:{color};'>{icon} {act.status}</div>", unsafe_allow_html=True)

        last_obs = get_last_obs(act.id)
        if last_obs:
            c_obs.markdown(f"<div style='padding-top:6px;font-size:11px;color:#64748B;font-style:italic;'>💬 {last_obs[:55]}{'...' if len(last_obs)>55 else ''}</div>", unsafe_allow_html=True)

        with c_btn:
            if is_admin():
                if act.status == "PENDIENTE":
                    if st.button("▶ Iniciar", key=f"ini_{act.id}", use_container_width=True):
                        st.session_state.accion_pendiente = {"id": act.id, "accion": "iniciar", "estado_actual": act.status, "nombre": act.activity_name, "numero": act.activity_number}
                        st.rerun()
                elif act.status == "EN PROGRESO":
                    if st.button("✅ Completar", key=f"comp_{act.id}", use_container_width=True):
                        st.session_state.accion_pendiente = {"id": act.id, "accion": "completar", "estado_actual": act.status, "nombre": act.activity_name, "numero": act.activity_number}
                        st.rerun()
                elif act.status == "COMPLETADO":
                    if st.button("↩ Reabrir", key=f"reab_{act.id}", use_container_width=True):
                        st.session_state.accion_pendiente = {"id": act.id, "accion": "reabrir", "estado_actual": act.status, "nombre": act.activity_name, "numero": act.activity_number}
                        st.rerun()
            else:
                c_btn.markdown("<div style='padding-top:8px;font-size:11px;color:#CBD5E1;'>Solo admin</div>", unsafe_allow_html=True)

    st.markdown("---")
