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
from app.components import (
    render_sidebar, render_page_header,
    render_no_permission_warning, status_badge
)
from app.database import (
    get_activities, get_project_config, bulk_update_statuses, get_user_note, save_user_note
)
from app.models import STATUSES, RESPONSABLES, FASES, STATUS_BADGE_CSS, RESPONSABLE_COLORS
from app.utils import activities_to_dataframe

# ── Auth guard ────────────────────────────────────────────────
require_auth()
inject_global_css()
render_sidebar()

# ── Datos ─────────────────────────────────────────────────────
config   = get_project_config()
scenario = config.scenario

activities = get_activities(scenario)

render_page_header(
    "Cronograma",
    f"Gestión de actividades · {scenario} · {len(activities)} actividades en 5 fases"
)

# ── Filtros ───────────────────────────────────────────────────
st.markdown('<div class="section-title">Filtros</div>', unsafe_allow_html=True)

fcol1, fcol2, fcol3, fcol4 = st.columns(4, gap="medium")

with fcol1:
    fase_opts = ["Todas las fases"] + [f"FASE {fn} · {fn}" for fn in range(5)]
    fase_labels = ["Todas las fases"] + [f"FASE {fn}" for fn in range(5)]
    selected_fase = st.selectbox("Fase", fase_labels, index=0)

with fcol2:
    resp_opts = ["Todos"] + RESPONSABLES
    selected_resp = st.selectbox("Responsable", resp_opts, index=0)

with fcol3:
    stat_opts = ["Todos"] + STATUSES
    selected_stat = st.selectbox("Estado", stat_opts, index=0)

with fcol4:
    search_text = st.text_input("Buscar actividad", placeholder="Escribe para buscar...")

# ── Aplicar filtros ───────────────────────────────────────────
filtered = activities

if selected_fase != "Todas las fases":
    fn_num = int(selected_fase.split(" ")[1])
    filtered = [a for a in filtered if a.fase_number == fn_num]

if selected_resp != "Todos":
    filtered = [a for a in filtered if a.responsable == selected_resp]

if selected_stat != "Todos":
    filtered = [a for a in filtered if a.status == selected_stat]

if search_text:
    filtered = [a for a in filtered if search_text.lower() in a.activity_name.lower()]

# ── Contador de resultados ────────────────────────────────────
cnt_pend = sum(1 for a in filtered if a.status == "PENDIENTE")
cnt_prog = sum(1 for a in filtered if a.status == "EN PROGRESO")
cnt_done = sum(1 for a in filtered if a.status == "COMPLETADO")

st.markdown(f"""
<div style="display:flex;gap:12px;align-items:center;margin:8px 0 20px 0;flex-wrap:wrap;">
    <span style="font-size:13px;color:#64748B;">
        Mostrando <strong style="color:#003A70;">{len(filtered)}</strong> actividades
    </span>
    <span class="badge badge-pendiente">⚪ {cnt_pend} pendientes</span>
    <span class="badge badge-progreso">🟡 {cnt_prog} en progreso</span>
    <span class="badge badge-completado">✅ {cnt_done} completadas</span>
</div>
""", unsafe_allow_html=True)

if not filtered:
    st.markdown('<div class="info-box">No hay actividades que coincidan con los filtros seleccionados.</div>', unsafe_allow_html=True)
    st.stop()

# ── Tabla editable ────────────────────────────────────────────
st.markdown('<div class="section-title">Actividades</div>', unsafe_allow_html=True)

can_edit = is_admin()
if not can_edit:
    render_no_permission_warning()
    st.markdown("<br>", unsafe_allow_html=True)

# Construir DataFrame
df = activities_to_dataframe(filtered)
df_display = df[["activity_number", "fase_name", "activity_name", "responsable", "status", "semanas", "notes"]].copy()
df_display.columns = ["#", "Fase", "Actividad", "Responsable", "Estado", "Semanas", "Notas"]

# Mapear IDs para recuperar después
id_map = {(row["activity_number"]): row["id"] for _, row in df.iterrows()}
original_statuses = {row["id"]: row["status"] for _, row in df.iterrows()}

col_config = {
    "#":           st.column_config.NumberColumn(width="small", disabled=True),
    "Fase":        st.column_config.TextColumn(width="medium", disabled=True),
    "Actividad":   st.column_config.TextColumn(width="large", disabled=True),
    "Responsable": st.column_config.TextColumn(width="small", disabled=True),
    "Estado":      st.column_config.SelectboxColumn(
                       width="medium",
                       options=STATUSES,
                       required=True,
                       disabled=not can_edit,
                   ),
    "Semanas":     st.column_config.TextColumn(width="small", disabled=True),
    "Notas":       st.column_config.TextColumn(width="large", disabled=True),
}

edited_df = st.data_editor(
    df_display,
    column_config=col_config,
    hide_index=True,
    use_container_width=True,
    key="activity_editor",
    num_rows="fixed",
)

# ── Detección de cambios y guardado ──────────────────────────
if can_edit:
    st.markdown("<br>", unsafe_allow_html=True)
    save_col, _, msg_col = st.columns([1, 2, 2])

    # Detectar cambios comparando con original
    changes = []
    for i, (_, row) in enumerate(edited_df.iterrows()):
        orig_row  = df.iloc[i]
        act_id    = orig_row["id"]
        new_status = row["Estado"]
        old_status = original_statuses.get(act_id, "PENDIENTE")
        if new_status != old_status:
            changes.append({"id": act_id, "new_status": new_status, "old_status": old_status})

    with save_col:
        btn_label = f"💾 Guardar {len(changes)} cambio(s)" if changes else "💾 Sin cambios"
        save_btn  = st.button(btn_label, disabled=(len(changes) == 0), use_container_width=True)

    if save_btn and changes:
        with st.spinner("Guardando..."):
            n = bulk_update_statuses(changes)
        if n == len(changes):
            st.success(f"✅ {n} actividad(es) actualizada(s) correctamente.")
        else:
            st.warning(f"⚠️ Se actualizaron {n} de {len(changes)} actividades.")
        st.rerun()

# ── Detalle de actividad (expandible) ────────────────────────
st.markdown('<div class="section-title">Detalle de actividad</div>', unsafe_allow_html=True)
st.markdown('<div class="info-box">Selecciona una actividad para ver sus notas y agregar comentarios personales.</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
act_names    = [f"#{a.activity_number} — {a.activity_name}" for a in filtered]
selected_act = st.selectbox("Actividad", act_names, label_visibility="collapsed")

if selected_act:
    idx     = act_names.index(selected_act)
    act     = filtered[idx]
    note    = get_user_note(act.id)

    dc1, dc2 = st.columns([1, 1], gap="large")
    with dc1:
        st.markdown(f"""
        <div style="background:#F8FAFC;border-radius:10px;padding:16px 18px;border:1px solid #E2E8F0;">
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;
                        color:#94A3B8;margin-bottom:8px;">Actividad #{act.activity_number}</div>
            <div style="font-size:15px;font-weight:600;color:#003A70;margin-bottom:12px;">{act.activity_name}</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;">
                <span class="badge badge-{'completado' if act.status=='COMPLETADO' else 'progreso' if act.status=='EN PROGRESO' else 'pendiente'}">{act.status}</span>
                <span style="background:#EFF6FF;color:#1D4ED8;font-size:11px;font-weight:600;
                             padding:3px 10px;border-radius:20px;">{act.responsable}</span>
                <span style="background:#F1F5F9;color:#475569;font-size:11px;font-weight:600;
                             padding:3px 10px;border-radius:20px;">S{act.week_start}–S{act.week_end}</span>
            </div>
            <div style="font-size:13px;color:#64748B;line-height:1.6;">
                <strong>Fase:</strong> {act.fase_name}<br>
                <strong>Dependencias:</strong> {act.notes or '—'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with dc2:
        st.markdown("**📝 Mis notas privadas**")
        new_note = st.text_area(
            "Nota",
            value=note,
            placeholder="Agrega tus notas personales sobre esta actividad...",
            height=120,
            label_visibility="collapsed",
        )
        if st.button("Guardar nota", key="save_note"):
            if save_user_note(act.id, new_note):
                st.success("Nota guardada.")
