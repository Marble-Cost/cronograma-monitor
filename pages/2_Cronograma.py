import streamlit as st

st.set_page_config(
    page_title="Cronograma · Compliance Monitor",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.auth import require_auth, is_admin
from app.styles import inject_global_css
from app.components import render_sidebar, render_page_header
from app.database import get_activities, get_project_config, update_activity_status, get_activity_log
from app.models import STATUSES, RESPONSABLES

require_auth()
inject_global_css()
render_sidebar()

@st.cache_data(ttl=30)
def get_all_observations(scenario: str) -> dict:
    try:
        from app.auth import get_supabase_client
        client = get_supabase_client()
        res = (client.table("activity_log")
               .select("activity_id, observation, changed_at")
               .not_.is_("observation", "null")
               .order("changed_at", desc=True).execute())
        seen, result = {}, {}
        for row in (res.data or []):
            aid = row["activity_id"]
            if aid not in seen:
                seen[aid]   = True
                result[aid] = row.get("observation", "") or ""
        return result
    except Exception:
        return {}

config = get_project_config()
render_page_header("📋 Cronograma", "Gestión de actividades · Selecciona el escenario a visualizar")

with st.expander("📖 Guía de uso", expanded=False):
    st.markdown("""
    **Estados:** ⚪ PENDIENTE · 🟡 EN PROGRESO · ✅ COMPLETADO

    **Acciones disponibles:**
    - **▶ Iniciar** — Marca la actividad como en ejecución
    - **✅ Completar** — Marca la actividad como finalizada
    - **↩ Reabrir** — Devuelve a EN PROGRESO si fue marcada por error
    - **📋 Historial** — Muestra todo el registro de cambios de esa actividad

    **Observaciones:** Al hacer clic en cualquier botón de acción, se abre un panel donde puedes dejar
    una nota describiendo qué ocurrió. Esa nota queda guardada permanentemente y es visible en la tabla.

    **Responsables:** 👨‍💻 Desarrollador · 🖥️ TI · 🤝 Ambos · 👔 Liderazgo
    """)

st.markdown("---")

sc1, sc2 = st.columns([2, 5])
with sc1:
    scenario = st.radio("🖥️ Escenario", ["Supabase", "SQL Server"],
                        index=0 if config.scenario == "Supabase" else 1, horizontal=True)
with sc2:
    if scenario == "Supabase":
        st.info("☁️ **Supabase** — Despliegue en nube. Requiere aprobación legal/seguridad de TI.")
    else:
        st.info("🖥️ **SQL Server** — Servidor corporativo interno. Requiere coordinación con TI.")

st.markdown("---")

fc1, fc2, fc3, fc4 = st.columns(4, gap="medium")
with fc1:
    sel_fase = st.selectbox("Fase", ["Todas las fases","FASE 0","FASE 1","FASE 2","FASE 3","FASE 4"])
with fc2:
    sel_resp = st.selectbox("Responsable", ["Todos"] + RESPONSABLES)
with fc3:
    sel_stat = st.selectbox("Estado", ["Todos"] + STATUSES)
with fc4:
    buscar = st.text_input("Buscar", placeholder="Nombre de actividad...")

all_activities = get_activities(scenario)
observations   = get_all_observations(scenario)

activities = all_activities
if sel_fase != "Todas las fases":
    fn = int(sel_fase.split(" ")[1])
    activities = [a for a in activities if a.fase_number == fn]
if sel_resp != "Todos":
    activities = [a for a in activities if a.responsable == sel_resp]
if sel_stat != "Todos":
    activities = [a for a in activities if a.status == sel_stat]
if buscar:
    activities = [a for a in activities if buscar.lower() in a.activity_name.lower()]

total      = len(all_activities)
pct_global = int(sum(1 for a in all_activities if a.status == "COMPLETADO") / total * 100) if total else 0
n_pend     = sum(1 for a in activities if a.status == "PENDIENTE")
n_prog     = sum(1 for a in activities if a.status == "EN PROGRESO")
n_done     = sum(1 for a in activities if a.status == "COMPLETADO")

st.markdown(f"**Progreso global {scenario}: {pct_global}%** · mostrando {len(activities)} actividades · ⚪ {n_pend} · 🟡 {n_prog} · ✅ {n_done}")
st.progress(pct_global / 100)
st.markdown("---")

if not activities:
    st.info("No hay actividades que coincidan con los filtros.")
    st.stop()

# ── Estado de sesión ──────────────────────────────────────────
if "accion_pendiente" not in st.session_state:
    st.session_state.accion_pendiente = None
if "ver_historial" not in st.session_state:
    st.session_state.ver_historial = None

# ── Panel de confirmación ─────────────────────────────────────
if st.session_state.accion_pendiente:
    ap           = st.session_state.accion_pendiente
    nuevo_estado = {"iniciar": "EN PROGRESO", "completar": "COMPLETADO", "reabrir": "EN PROGRESO"}[ap["accion"]]
    icono        = {"iniciar": "▶", "completar": "✅", "reabrir": "↩"}[ap["accion"]]

    st.info(f"{icono} **Confirmando** — #{ap['numero']} {ap['nombre'][:55]}  \n**{ap['estado_actual']}** → **{nuevo_estado}**")

    obs = st.text_area("📝 Observación (queda guardada permanentemente)",
        placeholder="Describe qué ocurrió, qué se entregó, o por qué se realiza este cambio...",
        height=80, key="obs_input")

    cc1, cc2, _ = st.columns([1, 1, 4])
    with cc1:
        if st.button("✅ Confirmar", type="primary", use_container_width=True):
            ok = update_activity_status(ap["id"], nuevo_estado, ap["estado_actual"], obs.strip() or None)
            if ok:
                st.success(f"✅ Actualizado a **{nuevo_estado}**")
                st.session_state.accion_pendiente = None
                st.cache_data.clear()
                st.rerun()
    with cc2:
        if st.button("✗ Cancelar", use_container_width=True):
            st.session_state.accion_pendiente = None
            st.rerun()
    st.markdown("---")

# ── Panel de historial ────────────────────────────────────────
if st.session_state.ver_historial:
    vh = st.session_state.ver_historial
    st.markdown(f"#### 📋 Historial completo — #{vh['numero']} {vh['nombre'][:60]}")
    logs = get_activity_log(vh["id"])
    if not logs:
        st.info("Esta actividad no tiene cambios registrados todavía.")
    else:
        for log in logs:
            changed_at = log.get("changed_at", "")[:16].replace("T", " ")
            user_email = log.get("user_email", "—")
            old_s      = log.get("old_status", "—")
            new_s      = log.get("new_status", "—")
            obs        = log.get("observation", "")
            icon_new   = {"PENDIENTE": "⚪", "EN PROGRESO": "🟡", "COMPLETADO": "✅"}.get(new_s, "•")
            obs_html   = f"<br><em style='color:#64748B;'>💬 {obs}</em>" if obs else ""
            st.markdown(f"""
            <div style="padding:8px 0;border-bottom:1px solid #F1F5F9;">
                <span style="font-size:11px;color:#94A3B8;">{changed_at}</span>
                <span style="margin:0 8px;">{icon_new} <strong>{new_s}</strong></span>
                <span style="font-size:12px;color:#64748B;">({old_s} → {new_s}) · {user_email}</span>
                {obs_html}
            </div>
            """, unsafe_allow_html=True)
    if st.button("✗ Cerrar historial"):
        st.session_state.ver_historial = None
        st.rerun()
    st.markdown("---")

# ── Tabla ─────────────────────────────────────────────────────
STATUS_ICON  = {"PENDIENTE": "⚪", "EN PROGRESO": "🟡", "COMPLETADO": "✅"}
RESP_ICON    = {"Desarrollador": "👨‍💻", "TI": "🖥️", "Ambos": "🤝", "Liderazgo": "👔"}
STATUS_COLOR = {"PENDIENTE": "#94A3B8", "EN PROGRESO": "#D97706", "COMPLETADO": "#16A34A"}

for fase_num in sorted(set(a.fase_number for a in activities)):
    fase_acts        = [a for a in activities if a.fase_number == fase_num]
    completadas_fase = sum(1 for a in fase_acts if a.status == "COMPLETADO")
    pct_fase         = int(completadas_fase / len(fase_acts) * 100)

    st.markdown(f"#### {fase_acts[0].fase_name} &nbsp; `{pct_fase}%`")
    st.progress(pct_fase / 100)

    h0,h1,h2,h3,h4,h5,h6,h7 = st.columns([0.5,3.2,1.1,0.8,1.2,2.2,1.2,1.0], gap="small")
    for h, t in zip([h0,h1,h2,h3,h4,h5,h6,h7],
                    ["#","ACTIVIDAD","RESPONSABLE","SEMANAS","ESTADO","ÚLTIMA OBS.","ACCIÓN","HISTORIAL"]):
        h.markdown(f"<div style='font-size:10px;color:#94A3B8;font-weight:600;'>{t}</div>", unsafe_allow_html=True)

    for act in fase_acts:
        color = STATUS_COLOR.get(act.status, "#94A3B8")
        c0,c1,c2,c3,c4,c5,c6,c7 = st.columns([0.5,3.2,1.1,0.8,1.2,2.2,1.2,1.0], gap="small")

        c0.markdown(f"<div style='padding-top:8px;color:#94A3B8;font-size:12px;'>#{act.activity_number}</div>", unsafe_allow_html=True)
        c1.markdown(f"<div style='padding-top:8px;font-size:13px;font-weight:500;'>{act.activity_name}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='padding-top:8px;font-size:12px;'>{RESP_ICON.get(act.responsable,'')} {act.responsable}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='padding-top:8px;font-size:12px;color:#64748B;'>S{act.week_start}–S{act.week_end}</div>", unsafe_allow_html=True)
        c4.markdown(f"<div style='padding-top:8px;font-size:12px;font-weight:600;color:{color};'>{STATUS_ICON.get(act.status,'')} {act.status}</div>", unsafe_allow_html=True)

        last_obs = observations.get(act.id, "")
        if last_obs:
            c5.markdown(f"<div style='padding-top:6px;font-size:11px;color:#64748B;font-style:italic;'>💬 {last_obs[:50]}{'...' if len(last_obs)>50 else ''}</div>", unsafe_allow_html=True)

        with c6:
            if is_admin():
                if act.status == "PENDIENTE":
                    if st.button("▶ Iniciar", key=f"ini_{act.id}", use_container_width=True):
                        st.session_state.accion_pendiente = {"id": act.id, "accion": "iniciar", "estado_actual": act.status, "nombre": act.activity_name, "numero": act.activity_number}
                        st.session_state.ver_historial = None
                        st.rerun()
                elif act.status == "EN PROGRESO":
                    if st.button("✅ Completar", key=f"comp_{act.id}", use_container_width=True):
                        st.session_state.accion_pendiente = {"id": act.id, "accion": "completar", "estado_actual": act.status, "nombre": act.activity_name, "numero": act.activity_number}
                        st.session_state.ver_historial = None
                        st.rerun()
                elif act.status == "COMPLETADO":
                    if st.button("↩ Reabrir", key=f"reab_{act.id}", use_container_width=True):
                        st.session_state.accion_pendiente = {"id": act.id, "accion": "reabrir", "estado_actual": act.status, "nombre": act.activity_name, "numero": act.activity_number}
                        st.session_state.ver_historial = None
                        st.rerun()
            else:
                st.markdown("<div style='padding-top:8px;font-size:11px;color:#CBD5E1;'>Solo admin</div>", unsafe_allow_html=True)

        with c7:
            if st.button("📋", key=f"hist_{act.id}", use_container_width=True, help="Ver historial completo"):
                st.session_state.ver_historial = {"id": act.id, "nombre": act.activity_name, "numero": act.activity_number}
                st.session_state.accion_pendiente = None
                st.rerun()

    st.markdown("---")
