from dataclasses import dataclass, field
from datetime import date
from typing import Optional


# ── Constantes ───────────────────────────────────────────────

SCENARIOS = ["SQL Server", "Supabase"]

STATUSES = ["PENDIENTE", "EN PROGRESO", "COMPLETADO"]

RESPONSABLES = ["Desarrollador", "TI", "Ambos", "Liderazgo"]

ROLES = ["analista", "supervisor", "administrador"]

FASES = {
    0: "FASE 0 · Alineación y Arranque",
    1: "FASE 1 · Base de Datos",
    2: "FASE 2 · Backend Python",
    3: "FASE 3 · Frontend y Seguridad",
    4: "FASE 4 · Testing y Despliegue",
}

FASE_TOTALS = {0: 5, 1: 6, 2: 5, 3: 4, 4: 5}

STATUS_COLORS = {
    "PENDIENTE":   "#CBD5E1",
    "EN PROGRESO": "#FCD34D",
    "COMPLETADO":  "#4ADE80",
}

STATUS_BADGE_CSS = {
    "PENDIENTE":   "badge-pendiente",
    "EN PROGRESO": "badge-progreso",
    "COMPLETADO":  "badge-completado",
}

RESPONSABLE_COLORS = {
    "Desarrollador": "#DBEAFE",
    "TI":            "#D1FAE5",
    "Ambos":         "#FEF3C7",
    "Liderazgo":     "#EDE9FE",
}

SEMAFORO = {
    "PENDIENTE":   ("⚪", "sem-pending",  "Pendiente"),
    "EN PROGRESO": ("🟡", "sem-progress", "En progreso"),
    "COMPLETADO":  ("🟢", "sem-done",     "Completado"),
}


# ── Dataclasses ───────────────────────────────────────────────

@dataclass
class Activity:
    id: int
    scenario: str
    fase_number: int
    fase_name: str
    activity_number: int
    activity_name: str
    responsable: str
    status: str
    week_start: int
    week_end: int
    notes: str = ""
    updated_by: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "Activity":
        return cls(
            id             = d.get("id", 0),
            scenario       = d.get("scenario", ""),
            fase_number    = d.get("fase_number", 0),
            fase_name      = d.get("fase_name", ""),
            activity_number= d.get("activity_number", 0),
            activity_name  = d.get("activity_name", ""),
            responsable    = d.get("responsable", ""),
            status         = d.get("status", "PENDIENTE"),
            week_start     = d.get("week_start", 1),
            week_end       = d.get("week_end", 1),
            notes          = d.get("notes", "") or "",
            updated_by     = d.get("updated_by"),
            updated_at     = d.get("updated_at"),
        )


@dataclass
class ProjectConfig:
    id: int = 1
    project_name: str = "Compliance Monitor · Sofgen Pharma"
    start_date: Optional[date] = None
    scenario: str = "Supabase"
    total_weeks: int = 12

    @classmethod
    def from_dict(cls, d: dict) -> "ProjectConfig":
        sd = d.get("start_date")
        if isinstance(sd, str) and sd:
            from datetime import datetime
            try:
                sd = datetime.strptime(sd, "%Y-%m-%d").date()
            except Exception:
                sd = None
        return cls(
            id           = d.get("id", 1),
            project_name = d.get("project_name", "Compliance Monitor · Sofgen Pharma"),
            start_date   = sd,
            scenario     = d.get("scenario", "Supabase"),
            total_weeks  = d.get("total_weeks", 12),
        )


@dataclass
class KPIData:
    pending:    int = 0
    in_progress: int = 0
    completed:  int = 0
    total:      int = 25

    @property
    def pct_completed(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.completed / self.total * 100, 1)

    @property
    def pct_in_progress(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.in_progress / self.total * 100, 1)
