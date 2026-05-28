import streamlit as st
from supabase import create_client, Client


def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    client = create_client(url, key)
    if st.session_state.get("sb_access_token") and st.session_state.get("sb_refresh_token"):
        try:
            client.auth.set_session(
                st.session_state["sb_access_token"],
                st.session_state["sb_refresh_token"],
            )
        except Exception:
            _clear_session()
    return client


def login_user(email: str, password: str) -> tuple[bool, str | None]:
    try:
        client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res.user and res.session:
            st.session_state["sb_access_token"]  = res.session.access_token
            st.session_state["sb_refresh_token"] = res.session.refresh_token
            st.session_state["sb_user_email"]    = res.user.email
            st.session_state["sb_user_id"]       = str(res.user.id)
            _load_profile(client, str(res.user.id))
            return True, None
        return False, "Credenciales inválidas"
    except Exception as e:
        msg = str(e)
        if "Invalid login" in msg or "invalid_credentials" in msg:
            return False, "Correo o contraseña incorrectos"
        return False, msg


def logout_user():
    try:
        get_supabase_client().auth.sign_out()
    except Exception:
        pass
    _clear_session()


def reset_password_for_email(email: str) -> tuple[bool, str | None]:
    """Envía correo de recuperación de contraseña."""
    try:
        client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
        client.auth.reset_password_for_email(email)
        return True, None
    except Exception as e:
        return False, str(e)


def update_password(new_password: str) -> tuple[bool, str | None]:
    """Actualiza la contraseña del usuario actualmente autenticado."""
    try:
        client = get_supabase_client()
        client.auth.update_user({"password": new_password})
        return True, None
    except Exception as e:
        return False, str(e)


def is_authenticated() -> bool:
    return bool(st.session_state.get("sb_access_token"))


def require_auth():
    if not is_authenticated():
        st.switch_page("main.py")


def get_current_user_id() -> str | None:
    return st.session_state.get("sb_user_id")


def get_current_user_email() -> str | None:
    return st.session_state.get("sb_user_email")


def get_current_user_name() -> str:
    return st.session_state.get("sb_full_name") or (
        st.session_state.get("sb_user_email", "Usuario").split("@")[0].title()
    )


def get_current_user_role() -> str:
    return st.session_state.get("sb_role", "usuario")


def is_admin() -> bool:
    return get_current_user_role() == "admin"


def _load_profile(client: Client, user_id: str):
    try:
        res = client.table("profiles").select("full_name, role").eq("id", user_id).single().execute()
        if res.data:
            st.session_state["sb_full_name"] = res.data.get("full_name", "")
            st.session_state["sb_role"]      = res.data.get("role", "usuario")
    except Exception:
        st.session_state["sb_role"] = "usuario"


def _clear_session():
    for key in ["sb_access_token", "sb_refresh_token", "sb_user_email",
                "sb_user_id", "sb_full_name", "sb_role"]:
        st.session_state.pop(key, None)
