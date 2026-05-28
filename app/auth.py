import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta

COOKIE_NAME = "cm_session"


@st.cache_resource
def _get_cookie_manager():
    import extra_streamlit_components as stx
    return stx.CookieManager()


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
            _store_session(res.user, res.session)
            _save_cookie(res.session.refresh_token)
            return True, None
        return False, "Credenciales inválidas"
    except Exception as e:
        msg = str(e)
        if "Invalid login" in msg or "invalid_credentials" in msg:
            return False, "Correo o contraseña incorrectos"
        return False, msg


def logout_user():
    try:
        client = get_supabase_client()
        client.auth.sign_out()
    except Exception:
        pass
    _clear_cookie()
    _clear_session()


def is_authenticated() -> bool:
    return bool(st.session_state.get("sb_access_token"))


def require_auth():
    """Verifica sesión activa. Si no hay, intenta restaurar desde cookie."""
    if is_authenticated():
        return
    if _restore_from_cookie():
        return
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


# ── Internos ──────────────────────────────────────────────────

def _store_session(user, session):
    st.session_state["sb_user"]          = user
    st.session_state["sb_access_token"]  = session.access_token
    st.session_state["sb_refresh_token"] = session.refresh_token
    st.session_state["sb_user_email"]    = user.email
    st.session_state["sb_user_id"]       = str(user.id)
    client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
    _load_profile(client, str(user.id))


def _load_profile(client: Client, user_id: str):
    try:
        res = client.table("profiles").select("full_name, role").eq("id", user_id).single().execute()
        if res.data:
            st.session_state["sb_full_name"] = res.data.get("full_name", "")
            st.session_state["sb_role"]      = res.data.get("role", "usuario")
    except Exception:
        st.session_state["sb_role"] = "usuario"


def _save_cookie(refresh_token: str):
    try:
        cm = _get_cookie_manager()
        expires = datetime.now() + timedelta(days=30)
        cm.set(COOKIE_NAME, refresh_token, expires_at=expires)
    except Exception:
        pass


def _clear_cookie():
    try:
        cm = _get_cookie_manager()
        cm.delete(COOKIE_NAME)
    except Exception:
        pass


def _restore_from_cookie() -> bool:
    try:
        cm = _get_cookie_manager()
        refresh_token = cm.get(COOKIE_NAME)
        if not refresh_token:
            return False
        client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
        res = client.auth.refresh_session(refresh_token)
        if res.user and res.session:
            _store_session(res.user, res.session)
            _save_cookie(res.session.refresh_token)
            return True
    except Exception:
        pass
    return False


def _clear_session():
    for key in ["sb_user", "sb_access_token", "sb_refresh_token",
                "sb_user_email", "sb_user_id", "sb_full_name", "sb_role"]:
        st.session_state.pop(key, None)
