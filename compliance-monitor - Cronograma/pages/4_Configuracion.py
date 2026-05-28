import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Configuración · Compliance Monitor",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.auth import require_auth, get_current_user_id, get_current_user_role, is_editor
from app.styles import inject_global_css
from app.components import render_sidebar, render_page_header
from app.database import (
    get_project_config, save_project_config,
    get_profile, update_profile_name,
    get_all_profiles, update_user_role,
    get_recent_log,
)
from app.models import SCENARIOS, ROLES
from app.utils import format_date_es, get_end_date

# ── Auth guard ────────────────────────────────────────────────
require_auth()
inject_global_css()
render_sidebar()

user_id = get_current_user_id()
role    = get_current_user_role()

render_page_header("Configuración", "Parámetros del proyecto, perfil de usuario y auditoría")

tabs = st.tabs(["⚙️ Proyecto", "👤 Mi Perfil", "📋 Historial", "👥 Usuarios"])

# ════════════════════════════════════════════════════════════
# TAB 1 — Configuración del proyecto
# ════════════════════════════════════════════════════════════
with tabs[0]:
    config = get_project_config()

    st.markdown('<div class="section-title">Parámetros del Proyecto</div>', unsafe_allow_html=True)

    if not is_editor():
        st.markdown("""
        <div class="info-box">
            🔒 Solo supervisores y administradores pueden modificar la configuración del proyecto.
        </div>
        """, unsafe_allow_html=True)

    cc1, cc2 = st.columns(2, gap="large")

    with cc1:
        # Fecha de inicio
        sd_val = config.start_date if config.start_date else None
        new_date = st.date_input(
            "📅 Fecha de inicio (Aprobación TI)",
            value=sd_val,
            min_value=date(2024, 1, 1),
            max_value=date(2030, 12, 31),
            help="Esta es la fecha desde la que se calculan todas las semanas del cronograma.",
            disabled=not is_editor(),
            format="YYYY-MM-DD",
        )

    with cc2:
        # Escenario
        scenario_idx = SCENARIOS.index(config.scenario) if config.scenario in SCENARIOS else 1
        new_scenario = st.radio(
            "🖥️ Escenario de despliegue",
            SCENARIOS,
            index=scenario_idx,
            disabled=not is_editor(),
            help="Selecciona el escenario técnico aprobado por TI.",
        )

    # Resumen de fechas calculadas
    if new_date:
        end_date    = get_end_date(new_date)
        st.markdown(f"""
        <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;
                    padding:14px 18px;margin-top:16px;">
            <div style="font-size:13px;color:#166534;font-weight:600;margin-bottom:8px;">
                📅 Fechas calculadas automáticamente
            </div>
            <div style="display:flex;gap:30px;flex-wrap:wrap;">
                <div>
                    <div style="font-size:11px;color:#4ADE80;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">Inicio</div>
                    <div style="font-size:15px;font-weight:700;color:#166534;">{format_date_es(new_date)}</div>
                </div>
                <div>
                    <div style="font-size:11px;color:#4ADE80;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">Fin estimado</div>
                    <div style="font-size:15px;font-weight:700;color:#166534;">{format_date_es(end_date)}</div>
                </div>
                <div>
                    <div style="font-size:11px;color:#4ADE80;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">Duración</div>
                    <div style="font-size:15px;font-weight:700;color:#166534;">12 semanas · 84 días</div>
                </div>
                <div>
                    <div style="font-size:11px;color:#4ADE80;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">Escenario</div>
                    <div style="font-size:15px;font-weight:700;color:#166534;">{new_scenario}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if is_editor():
        if st.button("💾 Guardar configuración del proyecto", type="primary"):
            save_d = new_date if isinstance(new_date, date) else None
            ok = save_project_config(save_d, new_scenario)
            if ok:
                st.success("✅ Configuración guardada. El cronograma se ha actualizado.")
                st.rerun()

    # Info boxes
    st.markdown("""
    <div class="warning-box" style="margin-top:16px;">
        ⚠️ <strong>Dependencia crítica</strong> — El cronograma solo arranca cuando TI apruebe 
        el proyecto formalmente. La <em>Fecha de inicio</em> debe corresponder a esa aprobación.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-box" style="margin-top:10px;">
        ℹ️ <strong>Escenario activo: {config.scenario}</strong> — 
        {'SQL Server requiere coordinación con TI para configurar el servidor corporativo interno.' 
         if config.scenario == 'SQL Server' 
         else 'Supabase requiere aprobación legal/seguridad para datos en nube externa (TI + Jurídica).'}
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB 2 — Mi Perfil
# ════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-title">Mi Perfil</div>', unsafe_allow_html=True)

    profile = get_profile(user_id) if user_id else {}

    pc1, pc2 = st.columns(2, gap="large")

    with pc1:
        current_name = profile.get("full_name", "")
        new_name = st.text_input("Nombre completo", value=current_name, placeholder="Tu nombre completo")
        st.text_input("Correo electrónico", value=profile.get("email", ""), disabled=True)
        st.text_input(
            "Rol en el sistema",
            value=profile.get("role", "analista").capitalize(),
            disabled=True,
            help="El rol es asignado por el administrador del sistema."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Actualizar nombre", key="update_name"):
            if new_name.strip():
                ok = update_profile_name(user_id, new_name.strip())
                if ok:
                    st.success("✅ Nombre actualizado.")
                    st.rerun()
            else:
                st.warning("El nombre no puede estar vacío.")

    with pc2:
        st.markdown(f"""
        <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:20px;">
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;
                        color:#94A3B8;margin-bottom:12px;">Resumen de acceso</div>
            <div style="font-size:32px;margin-bottom:8px;">
                {"👑" if role == "administrador" else "🔭" if role == "supervisor" else "👤"}
            </div>
            <div style="font-size:18px;font-weight:700;color:#003A70;text-transform:capitalize;
                        margin-bottom:4px;">{role}</div>
            <div style="font-size:13px;color:#64748B;line-height:1.6;margin-top:10px;">
                {"✅ Ver dashboard · Ver cronograma · <strong>Editar estados</strong> · <strong>Configurar proyecto</strong> · <strong>Gestionar usuarios</strong>" 
                 if role == "administrador" 
                 else "✅ Ver dashboard · Ver cronograma · <strong>Editar estados</strong> · <strong>Configurar proyecto</strong>" 
                 if role == "supervisor" 
                 else "✅ Ver dashboard · Ver cronograma · Ver Gantt · Agregar notas personales"}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB 3 — Historial de actividad
# ════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-title">Historial de Cambios</div>', unsafe_allow_html=True)
    st.markdown("Los últimos 20 cambios de estado registrados en el sistema.", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    logs = get_recent_log(20)

    if not logs:
        st.markdown('<div class="info-box">No hay registros de actividad todavía. Los cambios de estado aparecerán aquí.</div>', unsafe_allow_html=True)
    else:
        for log in logs:
            act_name  = "—"
            if log.get("activities"):
                act_name = log["activities"].get("activity_name", "—")[:50]

            changed_at = log.get("changed_at", "")[:16].replace("T", " ")
            user_email = log.get("user_email", "—")
            old_s = log.get("old_status", "—")
            new_s = log.get("new_status", "—")

            old_badge_css = {"PENDIENTE": "badge-pendiente", "EN PROGRESO": "badge-progreso", "COMPLETADO": "badge-completado"}.get(old_s, "badge-pendiente")
            new_badge_css = {"PENDIENTE": "badge-pendiente", "EN PROGRESO": "badge-progreso", "COMPLETADO": "badge-completado"}.get(new_s, "badge-pendiente")

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;
                        border-bottom:1px solid #F1F5F9;flex-wrap:wrap;">
                <span style="font-size:11px;color:#94A3B8;min-width:115px;">{changed_at}</span>
                <span style="font-size:13px;color:#003A70;font-weight:500;flex:1;min-width:180px;">{act_name}</span>
                <span class="badge {old_badge_css}" style="font-size:10px;">{old_s}</span>
                <span style="color:#94A3B8;">→</span>
                <span class="badge {new_badge_css}" style="font-size:10px;">{new_s}</span>
                <span style="font-size:11px;color:#94A3B8;">{user_email}</span>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB 4 — Gestión de usuarios (solo Admin)
# ════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-title">Gestión de Usuarios</div>', unsafe_allow_html=True)

    if role != "administrador":
        st.markdown("""
        <div class="warning-box">
            🔒 Solo el <strong>Administrador</strong> puede ver y modificar usuarios del sistema.
        </div>
        """, unsafe_allow_html=True)
    else:
        profiles = get_all_profiles()
        if not profiles:
            st.info("No se encontraron perfiles registrados.")
        else:
            st.markdown(f"Total de usuarios registrados: **{len(profiles)}**")
            st.markdown("<br>", unsafe_allow_html=True)

            for p in profiles:
                uc1, uc2, uc3 = st.columns([2, 1, 1], gap="medium")
                with uc1:
                    st.markdown(f"""
                    <div>
                        <div style="font-size:14px;font-weight:600;color:#003A70;">{p.get('full_name') or 'Sin nombre'}</div>
                        <div style="font-size:12px;color:#64748B;">{p.get('email', '—')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with uc2:
                    current_role = p.get("role", "analista")
                    new_role = st.selectbox(
                        "Rol",
                        ROLES,
                        index=ROLES.index(current_role) if current_role in ROLES else 0,
                        key=f"role_{p['id']}",
                        label_visibility="collapsed",
                    )
                with uc3:
                    if st.button("Actualizar", key=f"upd_{p['id']}", use_container_width=True):
                        if update_user_role(p["id"], new_role):
                            st.success(f"✅ Rol de {p.get('email','?')} actualizado.")
                            st.rerun()

                st.markdown('<hr style="border:none;border-top:1px solid #F1F5F9;margin:4px 0;">', unsafe_allow_html=True)
