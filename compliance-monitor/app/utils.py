from datetime import date, timedelta
from typing import Optional
import pandas as pd
from app.models import Activity, FASES, STATUS_COLORS, RESPONSABLE_COLORS


def week_to_date(start_date: date, week_number: int, day_offset: int = 0) -> date:
    """Convierte número de semana (1-12) a fecha real dado start_date."""
    return start_date + timedelta(weeks=week_number - 1, days=day_offset)


def get_week_label(start_date: Optional[date], week: int) -> str:
    if start_date:
        d = week_to_date(start_date, week)
        return d.strftime("%d/%m")
    return f"S{week}"


def get_current_week(start_date: Optional[date], total_weeks: int = 12) -> Optional[int]:
    if not start_date:
        return None
    today = date.today()
    if today < start_date:
        return None
    delta = (today - start_date).days
    week = delta // 7 + 1
    if week > total_weeks:
        return total_weeks
    return week


def activities_to_dataframe(activities: list[Activity]) -> pd.DataFrame:
    """Convierte lista de actividades a DataFrame para st.data_editor."""
    rows = []
    for a in activities:
        rows.append({
            "id":              a.id,
            "activity_number": a.activity_number,
            "fase_name":       a.fase_name,
            "activity_name":   a.activity_name,
            "responsable":     a.responsable,
            "status":          a.status,
            "semanas":         f"S{a.week_start}–S{a.week_end}",
            "notes":           a.notes,
        })
    return pd.DataFrame(rows)


def get_gantt_dataframe(activities: list[Activity], start_date: Optional[date] = None) -> pd.DataFrame:
    """Construye el DataFrame para el diagrama de Gantt."""
    rows = []
    for a in activities:
        if start_date:
            start = week_to_date(start_date, a.week_start)
            # Fin = inicio semana_end + 6 días (cubre toda la semana)
            finish = week_to_date(start_date, a.week_end, day_offset=6)
        else:
            # Sin fecha: usar números de semana como días proxy desde 2024-01-01
            from datetime import datetime
            base = datetime(2024, 1, 1).date()
            start  = base + timedelta(weeks=a.week_start - 1)
            finish = base + timedelta(weeks=a.week_end - 1, days=6)

        rows.append({
            "id":              a.id,
            "activity_number": a.activity_number,
            "label":           f"#{a.activity_number} {a.activity_name[:45]}",
            "fase":            a.fase_name,
            "responsable":     a.responsable,
            "status":          a.status,
            "start":           start,
            "finish":          finish,
            "color":           STATUS_COLORS.get(a.status, "#CBD5E1"),
            "week_start":      a.week_start,
            "week_end":        a.week_end,
        })
    return pd.DataFrame(rows)


def semaforo_fase(phase_data: dict) -> tuple[str, str]:
    """Devuelve (emoji, label) para el semáforo de una fase."""
    pct = phase_data["pct"]
    ip  = phase_data["in_progress"]
    if pct == 100:
        return "🟢", "Completada"
    if ip > 0 or pct > 0:
        return "🟡", "En progreso"
    return "⚪", "Pendiente"


def format_date_es(d: Optional[date]) -> str:
    if not d:
        return "No definida"
    MONTHS = ["ene", "feb", "mar", "abr", "may", "jun",
              "jul", "ago", "sep", "oct", "nov", "dic"]
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def get_end_date(start_date: Optional[date], total_weeks: int = 12) -> Optional[date]:
    if not start_date:
        return None
    return start_date + timedelta(weeks=total_weeks) - timedelta(days=1)
