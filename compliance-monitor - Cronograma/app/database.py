import streamlit as st
from datetime import datetime, date
from app.auth import get_supabase_client, get_current_user_id, get_current_user_email
from app.models import Activity, ProjectConfig, KPIData


# ── Activities ────────────────────────────────────────────────

def get_activities(scenario: str) -> list[Activity]:
    try:
        client = get_supabase_client()
        res = (
            client.table("activities")
            .select("*")
            .eq("scenario", scenario)
            .order("activity_number")
            .execute()
        )
        return [Activity.from_dict(r) for r in (res.data or [])]
    except Exception as e:
        st.error(f"Error cargando actividades: {e}")
        return []


def update_activity_status(activity_id: int, new_status: str, old_status: str) -> bool:
    user_id    = get_current_user_id()
    user_email = get_current_user_email()
    try:
        client = get_supabase_client()
        # Update activity
        client.table("activities").update({
            "status":     new_status,
            "updated_by": user_id,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", activity_id).execute()
        # Audit log
        client.table("activity_log").insert({
            "activity_id": activity_id,
            "user_id":     user_id,
            "user_email":  user_email,
            "old_status":  old_status,
            "new_status":  new_status,
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error actualizando actividad: {e}")
        return False


def bulk_update_statuses(changes: list[dict]) -> int:
    """changes = [{"id": int, "new_status": str, "old_status": str}]
    Returns number of successful updates."""
    count = 0
    for c in changes:
        if update_activity_status(c["id"], c["new_status"], c["old_status"]):
            count += 1
    return count


def get_kpis(scenario: str) -> KPIData:
    activities = get_activities(scenario)
    kpi = KPIData(total=len(activities))
    for a in activities:
        if a.status == "PENDIENTE":
            kpi.pending += 1
        elif a.status == "EN PROGRESO":
            kpi.in_progress += 1
        elif a.status == "COMPLETADO":
            kpi.completed += 1
    return kpi


def get_phase_progress(scenario: str) -> dict[int, dict]:
    """Returns {fase_number: {name, total, completed, in_progress, pct}}"""
    activities = get_activities(scenario)
    from app.models import FASES
    result: dict[int, dict] = {}
    for fn, fname in FASES.items():
        phase_acts = [a for a in activities if a.fase_number == fn]
        total       = len(phase_acts)
        completed   = sum(1 for a in phase_acts if a.status == "COMPLETADO")
        in_progress = sum(1 for a in phase_acts if a.status == "EN PROGRESO")
        pending     = total - completed - in_progress
        pct         = round(completed / total * 100) if total else 0
        result[fn]  = {
            "name":        fname,
            "total":       total,
            "completed":   completed,
            "in_progress": in_progress,
            "pending":     pending,
            "pct":         pct,
        }
    return result


# ── Project Config ────────────────────────────────────────────

def get_project_config() -> ProjectConfig:
    try:
        client = get_supabase_client()
        res = client.table("project_config").select("*").order("id").limit(1).execute()
        if res.data:
            return ProjectConfig.from_dict(res.data[0])
    except Exception as e:
        st.error(f"Error cargando configuración: {e}")
    return ProjectConfig()


def save_project_config(start_date: date | None, scenario: str) -> bool:
    try:
        client = get_supabase_client()
        config = get_project_config()
        payload = {
            "scenario":   scenario,
            "updated_at": datetime.utcnow().isoformat(),
        }
        if start_date:
            payload["start_date"] = start_date.isoformat()
        else:
            payload["start_date"] = None
        client.table("project_config").update(payload).eq("id", config.id).execute()
        return True
    except Exception as e:
        st.error(f"Error guardando configuración: {e}")
        return False


# ── User Profile ──────────────────────────────────────────────

def get_profile(user_id: str) -> dict:
    try:
        client = get_supabase_client()
        res = client.table("profiles").select("*").eq("id", user_id).single().execute()
        return res.data or {}
    except Exception:
        return {}


def update_profile_name(user_id: str, full_name: str) -> bool:
    try:
        client = get_supabase_client()
        client.table("profiles").update({
            "full_name":  full_name,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", user_id).execute()
        st.session_state["sb_full_name"] = full_name
        return True
    except Exception as e:
        st.error(f"Error actualizando perfil: {e}")
        return False


def get_all_profiles() -> list[dict]:
    """Solo para administradores."""
    try:
        client = get_supabase_client()
        res = client.table("profiles").select("id, email, full_name, role, created_at").execute()
        return res.data or []
    except Exception:
        return []


def update_user_role(user_id: str, new_role: str) -> bool:
    try:
        client = get_supabase_client()
        client.table("profiles").update({"role": new_role}).eq("id", user_id).execute()
        return True
    except Exception as e:
        st.error(f"Error actualizando rol: {e}")
        return False


# ── Activity Log ──────────────────────────────────────────────

def get_recent_log(limit: int = 20) -> list[dict]:
    try:
        client = get_supabase_client()
        res = (
            client.table("activity_log")
            .select("*, activities(activity_name, fase_name)")
            .order("changed_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


# ── User Notes ────────────────────────────────────────────────

def get_user_note(activity_id: int) -> str:
    user_id = get_current_user_id()
    if not user_id:
        return ""
    try:
        client = get_supabase_client()
        res = (
            client.table("user_notes")
            .select("note")
            .eq("activity_id", activity_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if res.data:
            return res.data[0].get("note", "")
    except Exception:
        pass
    return ""


def save_user_note(activity_id: int, note: str) -> bool:
    user_id = get_current_user_id()
    if not user_id:
        return False
    try:
        client = get_supabase_client()
        # Upsert: insert or update
        client.table("user_notes").upsert({
            "activity_id": activity_id,
            "user_id":     user_id,
            "note":        note,
            "updated_at":  datetime.utcnow().isoformat(),
        }, on_conflict="activity_id,user_id").execute()
        return True
    except Exception as e:
        st.error(f"Error guardando nota: {e}")
        return False
