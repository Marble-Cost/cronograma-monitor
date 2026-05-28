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
    get_recent_log,
)
from app.models import SCENARIOS
from app.utils import format_date_es, get_end_date

require_auth()
inject_global_css()
render_sidebar()

user_id = get_current_user_id()
role    = get_current_user_role()

render_page_header("Configuración", "Parámetros del proyecto, perfil y administración")

# Tabs — admin ve 4, usuario ve 3
if is_admin():
    tabs = st.tabs(["⚙️ Proyecto", "👤 Mi Perfil", "📋 Historial", "👥 Usuarios"])
else:
    tabs = st.tabs(["⚙️ Proyecto", "👤 Mi Perfil", "📋 Historial"])

# ── TAB 1: Proyecto ───────────────────────────────────────────
with tabs[0]:
    config = get_project_config()
    st.subheader("Parámetros del Proyecto")

    if not is_admin():
        st.info("🔒 Solo el administrador puede modificar la configuración del proyecto.")

    cc1, cc2 = st.columns(2, gap="large")
    with cc1:
        new_date = st.date_input(
            "📅 Fecha de inicio",
            value=config.start_date,
            min_value=date(2024, 1, 1),
            max_value=date(2030, 12, 31),
            disabled=not is_admin(),
            format="YYYY-MM-DD",
        )
    with cc2:
        scenario_idx = SCENARIOS.index(config.scenario) if config.scenario in SCENARIOS else 1
        new_scenario = st.radio(
            "🖥️ Escenario",
            SCENARIOS,
            index=scenario_idx,
            disabled=not is_admin(),
        )

    if new_date and is_admin():
        end_date = get_end_date(new_date)
        st.success(f"📅 Inicio: **{format_date_es(new_date)}** → Fin estimado: **{format_date_es(end_date)}** · 12 semanas")

    if is_admin():
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Guardar configuración", type="primary"):
            save_d = new_date if isinstance(new_date, date) else None
            if save_project_config(save_d, new_scenario):
                st.success("✅ Configuración guardada.")
                st.rerun()

# ── TAB 2: Mi Perfil ──────────────────────────────────────────
with tabs[1]:
    st.subheader("Mi Perfil")
    profile = get_profile(user_id) if user_id else {}

    pc1, pc2 = st.columns(2, gap="large")
    with pc1:
        current_name = profile.get("full_name", "")
        new_name = st.text_input("Nombre completo", value=current_name)
        st.text_input("Correo", value=profile.get("email", ""), disabled=True)
        st.text_input("Rol", value=role.capitalize(), disabled=True)

        if st.button("💾 Actualizar nombre"):
            if new_name.strip():
                if update_profile_name(user_id, new_name.strip()):
                    st.success("✅ Nombre actualizado.")
                    st.rerun()
            else:
                st.warning("El nombre no puede estar vacío.")

    with pc2:
        icon = "👑" if role == "admin" else "👤"
        permisos = (
            "✅ Ver todo · Editar estados · Configurar proyecto · Gestionar usuarios"
            if role == "admin"
            else "✅ Ver dashboard · Ver cronograma · Ver Gantt · Agregar notas"
        )
        st.markdown(f"""
        **{icon} Rol: {role.capitalize()}**
        
        {permisos}
        """)

# ── TAB 3: Historial ──────────────────────────────────────────
with tabs[2]:
    st.subheader("Historial de Cambios")
    logs = get_recent_log(20)

    if not logs:
        st.info("No hay registros todavía.")
    else:
        for log in logs:
            act_name   = "—"
            if log.get("activities"):
                act_name = log["activities"].get("activity_name", "—")[:50]
            changed_at = log.get("changed_at", "")[:16].replace("T", " ")
            user_email = log.get("user_email", "—")
            old_s      = log.get("old_status", "—")
            new_s      = log.get("new_status", "—")
            st.markdown(f"`{changed_at}` · **{act_name}** · {old_s} → **{new_s}** · _{user_email}_")
            st.divider()

# ── TAB 4: Usuarios (solo admin) ─────────────────────────────
if is_admin():
    with tabs[3]:
        st.subheader("Gestión de Usuarios")
        st.caption("Crea nuevos usuarios y gestiona sus roles.")

        # ── Crear usuario nuevo ───────────────────────────────
        st.markdown("#### ➕ Crear nuevo usuario")

        with st.form("create_user_form"):
            new_email    = st.text_input("Correo electrónico", placeholder="usuario@sofgen.com")
            new_password = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            new_fullname = st.text_input("Nombre completo", placeholder="Nombre Apellido")
            new_role     = st.selectbox("Rol", ["usuario", "admin"])
            create_btn   = st.form_submit_button("Crear usuario", type="primary")

        if create_btn:
            if not new_email or not new_password:
                st.error("Correo y contraseña son obligatorios.")
            elif len(new_password) < 6:
                st.error("La contraseña debe tener mínimo 6 caracteres.")
            else:
                from app.database import create_user_as_admin
                ok, msg = create_user_as_admin(new_email, new_password, new_fullname, new_role)
                if ok:
                    st.success(f"✅ Usuario {new_email} creado con rol {new_role}.")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {msg}")

        st.divider()

        # ── Lista de usuarios ─────────────────────────────────
        st.markdown("#### 👥 Usuarios registrados")
        profiles = get_all_profiles()

        if not profiles:
            st.info("No hay usuarios registrados.")
        else:
            for p in profiles:
                uc1, uc2, uc3 = st.columns([2, 1, 1], gap="medium")
                with uc1:
                    st.markdown(f"**{p.get('full_name') or 'Sin nombre'}**  \n{p.get('email', '—')}")
                with uc2:
                    current_role = p.get("role", "usuario")
                    new_role_val = st.selectbox(
                        "Rol", ["usuario", "admin"],
                        index=0 if current_role == "usuario" else 1,
                        key=f"role_{p['id']}",
                        label_visibility="collapsed",
                    )
                with uc3:
                    if st.button("Actualizar", key=f"upd_{p['id']}", use_container_width=True):
                        if update_user_role(p["id"], new_role_val):
                            st.success("✅ Rol actualizado.")
                            st.rerun()
                st.divider()
