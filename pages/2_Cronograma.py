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
from app.database import get_activities, get_project_config, update_activity_status, get_recent_log
from app.models import STATUSES, RESPONSABLES

require_auth()
inject_global_css()
render_sidebar()

config   = get_project_config()
scenario = config.scenario

render_page_header("📋 Cronograma", f"Gestión de actividades · Escenario: {scenario}")

# ── Guía de uso ───────────────────────────────────────────────
with st.expander("📖 Guía de uso — ¿Cómo funciona esta sección?", expanded=False):
    st.markdown("""
    **Esta sección es el centro de control del proyecto.** Desde aquí puedes ver y actualizar el estado de cada actividad.
    
    **Estados de actividad:**
    - ⚪ **PENDIENTE** — La actividad aún no ha comenzado
    - 🟡 **EN PROGRESO** — La actividad está siendo ejecutada actualmente
    - ✅ **COMPLETADO** — La actividad fue finalizada exitosamente
    
    **Cómo actualizar una actividad:**
    1. Localiza la actividad en la tabla (usa los filtros si hay muchas)
    2. Haz clic en el botón de acción de esa fila:
       - **▶ Iniciar** → cambia de PENDIENTE a EN PROGRESO
       - **✅ Completar** → cambia de EN PROGRESO a COMPLETADO
       - **↩ Reabrir** → devuelve a EN PROGRESO si fue completada por error
    3. Se abrirá un panel para dejar una observación (opcional pero recomendado)
    4. Confirma el cambio — quedará guardado permanentemente en la base de datos
    
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

# Contadores
n_pend = sum(1 for a in activities if a.status == "PENDIENTE")
n_prog = sum(1 for a in activities if a.status == "EN PROGRESO")
n_done = sum(1 for a in activities if a.status == "COMPLETADO")

st.markdown(f"**{len(activities)} actividades** · ⚪ {n_pend} pendientes · 🟡 {n_prog} en progreso · ✅ {n_done} completadas")
st.markdown("---")

if not activities:
    st.info("No hay actividades que coincidan con los filtros.")
    st.stop()

# ── Estado de la acción pendiente (modal) ─────────────────────
if "accion_pendiente" not in st.session_state:
    st.session_state.accion_pendiente = None

# ── Panel de confirmación ─────────────────────────────────────
if st.session_state.accion_pendiente:
    ap = st.session_state.accion_pendiente
    nuevo_estado = {
        "iniciar":   "EN PROGRESO",
        "completar": "COMPLETADO",
        "reabrir":   "EN PROGRESO",
    }[ap["accion"]]
    icono = {"iniciar": "▶", "completar": "✅", "reabrir": "↩"}[ap["accion"]]

    with st.container():
        st.markdown(f"""
        <div style="background:#EFF6FF;border:1.5px solid #BFDBFE;border-radius:12px;padding:20px 24px;margin-bottom:16px;">
            <div style="font-size:15px;font-weight:700;color:#1E40AF;margin-bottom:4px;">
                {icono} Confirmar acción — #{ap['numero']} {ap['nombre'][:60]}
            </div>
            <div style="font-size:13px;color:#3B82F6;">
                Estado actual: <strong>{ap['estado_actual']}</strong> → Nuevo estado: <strong>{nuevo_estado}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        obs = st.text_area(
            "📝 Observación (recomendado)",
            placeholder="Describe brevemente qué ocurrió, qué se entregó, o por qué se realiza este cambio...",
            height=90,
            key="obs_input"
        )

        cc1, cc2, _ = st.columns([1, 1, 3])
        with cc1:
            if st.button("✅ Confirmar cambio", type="primary", use_container_width=True):
                ok = update_activity_status(
                    ap["id"], nuevo_estado, ap["estado_actual"], obs.strip() or None
                )
                if ok:
                    st.success(f"✅ Actividad actualizada a **{nuevo_estado}**")
                    st.session_state.accion_pendiente = None
                    st.rerun()
        with cc2:
            if st.button("✗ Cancelar", use_container_width=True):
                st.session_state.accion_pendiente = None
                st.rerun()

    st.markdown("---")

# ── Tabla de actividades ──────────────────────────────────────
STATUS_ICON = {"PENDIENTE": "⚪", "EN PROGRESO": "🟡", "COMPLETADO": "✅"}
RESP_ICON   = {"Desarrollador": "👨‍💻", "TI": "🖥️", "Ambos": "🤝", "Liderazgo": "👔"}

for fase_num in sorted(set(a.fase_number for a in activities)):
    fase_acts = [a for a in activities if a.fase_number == fase_num]
    if not fase_acts:
        continue

    fase_name = fase_acts[0].fase_name
    completadas_fase = sum(1 for a in fase_acts if a.status == "COMPLETADO")
    pct_fase = int(completadas_fase / len(fase_acts) * 100)

    st.markdown(f"#### {fase_name} · {pct_fase}% completada")
    st.progress(pct_fase / 100)

    for act in fase_acts:
        icon   = STATUS_ICON.get(act.status, "⚪")
        rico   = RESP_ICON.get(act.responsable, "")

        col_num, col_name, col_resp, col_weeks, col_status, col_obs, col_btn = st.columns(
            [0.5, 3.5, 1.2, 0.8, 1.2, 2.5, 1.3], gap="small"
        )

        with col_num:
            st.markdown(f"<div style='padding-top:8px;color:#94A3B8;font-size:12px;'>#{act.activity_number}</div>", unsafe_allow_html=True)

        with col_name:
            st.markdown(f"<div style='padding-top:8px;font-size:13px;font-weight:500;color:#1E293B;'>{act.activity_name}</div>", unsafe_allow_html=True)

        with col_resp:
            st.markdown(f"<div style='padding-top:8px;font-size:12px;color:#475569;'>{rico} {act.responsable}</div>", unsafe_allow_html=True)

        with col_weeks:
            st.markdown(f"<div style='padding-top:8px;font-size:12px;color:#64748B;'>S{act.week_start}–S{act.week_end}</div>", unsafe_allow_html=True)

        with col_status:
            color = {"PENDIENTE": "#94A3B8", "EN PROGRESO": "#D97706", "COMPLETADO": "#16A34A"}.get(act.status, "#94A3B8")
            st.markdown(f"<div style='padding-top:8px;font-size:12px;font-weight:600;color:{color};'>{icon} {act.status}</div>", unsafe_allow_html=True)

        with col_obs:
            # Mostrar última observación si existe
            last_obs = _get_last_obs(act.id)
            if last_obs:
                st.markdown(f"<div style='padding-top:6px;font-size:11px;color:#64748B;font-style:italic;'>💬 {last_obs[:60]}{'...' if len(last_obs)>60 else ''}</div>", unsafe_allow_html=True)

        with col_btn:
            if is_admin():
                if act.status == "PENDIENTE":
                    if st.button("▶ Iniciar", key=f"ini_{act.id}", use_container_width=True):
                        st.session_state.accion_pendiente = {
                            "id": act.id, "accion": "iniciar",
                            "estado_actual": act.status,
                            "nombre": act.activity_name,
                            "numero": act.activity_number,
                        }
                        st.rerun()
                elif act.status == "EN PROGRESO":
                    if st.button("✅ Completar", key=f"comp_{act.id}", use_container_width=True):
                        st.session_state.accion_pendiente = {
                            "id": act.id, "accion": "completar",
                            "estado_actual": act.status,
                            "nombre": act.activity_name,
                            "numero": act.activity_number,
                        }
                        st.rerun()
                elif act.status == "COMPLETADO":
                    if st.button("↩ Reabrir", key=f"reab_{act.id}", use_container_width=True):
                        st.session_state.accion_pendiente = {
                            "id": act.id, "accion": "reabrir",
                            "estado_actual": act.status,
                            "nombre": act.activity_name,
                            "numero": act.activity_number,
                        }
                        st.rerun()
            else:
                st.markdown("<div style='padding-top:8px;font-size:11px;color:#CBD5E1;'>Solo admin</div>", unsafe_allow_html=True)

    st.markdown("---")


def _get_last_obs(activity_id: int) -> str:
    """Obtiene la última observación registrada para una actividad."""
    try:
        from app.database import get_supabase_via_auth
        client = get_supabase_via_auth()
        res = (client.table("activity_log")
               .select("observation")
               .eq("activity_id", activity_id)
               .not_.is_("observation", "null")
               .order("changed_at", desc=True)
               .limit(1)
               .execute())
        if res.data:
            return res.data[0].get("observation", "") or ""
    except Exception:
        pass
    return ""
