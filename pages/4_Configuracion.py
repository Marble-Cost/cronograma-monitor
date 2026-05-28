import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Configuración · Compliance Monitor",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.auth import require_auth, get_current_user_id, get_current_user_role, is_admin
from app.styles import inject_global_css
from app.components import render_sidebar, render_page_header
from app.database import (
    get_project_config, save_project_config,
    get_profile, update_profile_name,
    get_all_profiles, update_user_role,
    get_recent_log, create_user_as_admin,
)
from app.models import SCENARIOS
from app.utils import format_date_es, get_end_date, get_current_week

require_auth()
inject_global_css()
render_sidebar()

user_id = get_current_user_id()
role    = get_current_user_role()

render_page_header("⚙️ Configuración", "Ajustes del proyecto, perfil de usuario y administración")

tab_labels = ["📅 Proyecto", "👤 Mi Perfil", "📋 Historial"]
if is_admin():
    tab_labels.append("👥 Usuarios")

tabs = st.tabs(tab_labels)

# ════════════════════════════════════════════════════════════
# TAB 1 — Proyecto
# ════════════════════════════════════════════════════════════
with tabs[0]:
    config = get_project_config()
    st.subheader("Parámetros del Proyecto")
    st.caption("La fecha de inicio es el punto de referencia para todas las semanas del cronograma.")

    if not is_admin():
        st.info("🔒 Solo el administrador puede modificar la configuración.")

    cc1, cc2 = st.columns(2, gap="large")
    with cc1:
        new_date = st.date_input("📅 Fecha de inicio (aprobación de TI)",
            value=config.start_date, min_value=date(2024,1,1), max_value=date(2030,12,31),
            disabled=not is_admin(), format="YYYY-MM-DD",
            help="Todas las fechas del Gantt se calculan desde este día.")
    with cc2:
        idx = SCENARIOS.index(config.scenario) if config.scenario in SCENARIOS else 0
        new_scenario = st.radio("🖥️ Escenario activo", SCENARIOS, index=idx,
            disabled=not is_admin(),
            help="Define cuál escenario se muestra por defecto en Dashboard y Configuración.")

    if new_date and isinstance(new_date, date):
        end_date     = get_end_date(new_date)
        current_week = get_current_week(new_date)
        weeks_left   = (12 - current_week) if current_week else 12

        st.success(
            f"📅 Inicio: **{format_date_es(new_date)}** · "
            f"Fin estimado: **{format_date_es(end_date)}** · "
            f"Duración: **12 semanas** · "
            + (f"Semana actual: **S{current_week}** · **{weeks_left} semana(s) restante(s)**"
               if current_week else "El proyecto aún no ha comenzado según la fecha seleccionada.")
        )

    if is_admin():
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Guardar configuración", type="primary"):
            save_d = new_date if isinstance(new_date, date) else None
            if save_project_config(save_d, new_scenario):
                st.success("✅ Configuración guardada correctamente.")
                st.rerun()

    st.markdown("---")
    st.markdown("""
    **Guía del escenario:**
    - **Supabase** — Base de datos en la nube. Más rápido de implementar pero requiere aprobación legal para datos externos.
    - **SQL Server** — Servidor corporativo interno. Mayor control pero requiere más coordinación con TI.
    """)

# ════════════════════════════════════════════════════════════
# TAB 2 — Mi Perfil
# ════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("Mi Perfil")
    profile = get_profile(user_id) if user_id else {}

    pc1, pc2 = st.columns(2, gap="large")
    with pc1:
        new_name = st.text_input("Nombre completo", value=profile.get("full_name", ""),
                                  help="Este nombre aparece en el sidebar y en el historial de cambios.")
        st.text_input("Correo electrónico", value=profile.get("email", ""), disabled=True)
        st.text_input("Rol", value=role.capitalize(), disabled=True,
                      help="El rol es asignado por el administrador.")
        if st.button("💾 Actualizar nombre"):
            if new_name.strip():
                if update_profile_name(user_id, new_name.strip()):
                    st.success("✅ Nombre actualizado.")
                    st.rerun()
            else:
                st.warning("El nombre no puede estar vacío.")

    with pc2:
        icon    = "👑" if role == "admin" else "👤"
        perms   = ("✅ Ver todo · Editar estados · Configurar · Gestionar usuarios"
                   if role == "admin" else
                   "✅ Ver dashboard · Ver cronograma · Ver Gantt · Agregar notas privadas")
        st.markdown(f"### {icon} {role.capitalize()}")
        st.markdown(perms)

# ════════════════════════════════════════════════════════════
# TAB 3 — Historial
# ════════════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("Historial de Cambios")
    st.caption("Registro completo de todos los cambios de estado con sus observaciones.")
    logs = get_recent_log(30)

    if not logs:
        st.info("Aún no hay cambios registrados.")
    else:
        for log in logs:
            act_name   = "—"
            if log.get("activities"):
                act_name = log["activities"].get("activity_name", "—")[:55]
            changed_at = log.get("changed_at", "")[:16].replace("T", " ")
            user_email = log.get("user_email", "—")
            old_s      = log.get("old_status", "—")
            new_s      = log.get("new_status", "—")
            obs        = log.get("observation", "") or ""
            icon_new   = {"PENDIENTE": "⚪", "EN PROGRESO": "🟡", "COMPLETADO": "✅"}.get(new_s, "•")
            obs_html   = f"<br><em style='color:#64748B;font-size:11px;'>💬 {obs}</em>" if obs else ""
            st.markdown(f"""
            <div style="padding:10px 0;border-bottom:1px solid #F1F5F9;">
                <span style="font-size:11px;color:#94A3B8;">{changed_at}</span>
                <span style="margin:0 8px;font-size:13px;font-weight:600;">{icon_new} {act_name}</span>
                <span style="font-size:11px;color:#64748B;">{old_s} → <strong>{new_s}</strong> · {user_email}</span>
                {obs_html}
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 4 — Usuarios (solo admin)
# ════════════════════════════════════════════════════════════
if is_admin():
    with tabs[3]:
        st.subheader("Gestión de Usuarios")

        st.markdown("#### ➕ Crear nuevo usuario")
        with st.form("create_user_form"):
            nu_email    = st.text_input("Correo electrónico", placeholder="usuario@sofgen.com")
            nu_password = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            nu_name     = st.text_input("Nombre completo", placeholder="Nombre Apellido")
            nu_role     = st.selectbox("Rol", ["usuario", "admin"],
                help="usuario = solo puede ver · admin = puede editar y gestionar")
            create_btn  = st.form_submit_button("Crear usuario", type="primary")

        if create_btn:
            if not nu_email or not nu_password:
                st.error("Correo y contraseña son obligatorios.")
            elif len(nu_password) < 6:
                st.error("La contraseña debe tener mínimo 6 caracteres.")
            else:
                ok, msg = create_user_as_admin(nu_email, nu_password, nu_name, nu_role)
                if ok:
                    st.success(f"✅ Usuario **{nu_email}** creado con rol **{nu_role}**.")
                    st.rerun()
                else:
                    st.error(f"❌ Error al crear usuario: {msg}")

        st.markdown("---")
        st.markdown("#### 👥 Usuarios registrados")
        profiles = get_all_profiles()
        if not profiles:
            st.info("No hay usuarios registrados.")
        else:
            for p in profiles:
                uc1, uc2, uc3 = st.columns([2.5, 1.2, 1], gap="medium")
                with uc1:
                    fn = p.get("full_name") or "Sin nombre"
                    st.markdown(f"**{fn}**  \n{p.get('email','—')}")
                with uc2:
                    cr = p.get("role", "usuario")
                    new_r = st.selectbox("Rol", ["usuario","admin"],
                        index=0 if cr=="usuario" else 1,
                        key=f"role_{p['id']}", label_visibility="collapsed")
                with uc3:
                    if st.button("Actualizar", key=f"upd_{p['id']}", use_container_width=True):
                        if update_user_role(p["id"], new_r):
                            st.success("✅ Actualizado.")
                            st.rerun()
                st.divider()
