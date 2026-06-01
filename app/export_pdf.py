import io, os, base64
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

NAVY  = colors.HexColor("#003A70")
TEAL  = colors.HexColor("#00B5B0")
GREEN = colors.HexColor("#16A34A")
YELL  = colors.HexColor("#D97706")
RED   = colors.HexColor("#DC2626")
LGRAY = colors.HexColor("#F1F5F9")
DGRAY = colors.HexColor("#64748B")
WHITE = colors.white
BLACK = colors.black

def _style(size=10, bold=False, color=BLACK, align=TA_LEFT, leading=None):
    return ParagraphStyle("s", fontSize=size, fontName="Helvetica-Bold" if bold else "Helvetica",
                          textColor=color, alignment=align, leading=leading or size * 1.3)

def _salud(kpis, current_week):
    if kpis.pct_completed >= 100:
        return "🏆 PROYECTO COMPLETADO", GREEN
    if current_week:
        expected = (current_week / 12) * 100
        diff     = kpis.pct_completed - expected
        if diff >= 0:
            return "🟢 EN TIEMPO", GREEN
        elif diff >= -15:
            return "🟡 LIGERAMENTE ATRASADO", YELL
        else:
            return "🔴 EN RIESGO", RED
    return "⏸ SIN FECHA DE INICIO", DGRAY

def generate_pdf(activities, logs, kpis, phase_progress, config, scenario, atrasadas):
    from app.utils import get_current_week, format_date_es, get_end_date

    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=A4,
                               topMargin=1.5*cm, bottomMargin=1.8*cm,
                               leftMargin=1.8*cm, rightMargin=1.8*cm)
    story  = []
    W      = A4[0] - 3.6*cm
    today  = date.today()

    start_date   = config.start_date
    current_week = get_current_week(start_date)
    salud_label, salud_color = _salud(kpis, current_week)

    # ── Encabezado ────────────────────────────────────────────
    header_data = [[
        Paragraph("<b>COMPLIANCE MONITOR</b>", _style(18, bold=True, color=WHITE, align=TA_LEFT)),
        Paragraph(f"<b>SCHEDULE</b><br/><font size='9'>{scenario}</font>",
                  _style(11, bold=True, color=TEAL, align=TA_RIGHT)),
    ]]
    header_table = Table(header_data, colWidths=[W*0.65, W*0.35])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING",   (0,0), (-1,-1), 12),
        ("BOTTOMPADDING",(0,0), (-1,-1), 12),
        ("LEFTPADDING",  (0,0), (0,-1), 14),
        ("RIGHTPADDING", (-1,0),(-1,-1), 14),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))

    # Fecha y salud
    story.append(Paragraph(
        f"Informe generado el <b>{today.strftime('%d/%m/%Y')}</b>"
        + (f"  ·  Inicio del proyecto: <b>{format_date_es(start_date)}</b>"
           + (f"  ·  Semana actual: <b>S{current_week} de 12</b>" if current_week else "")
           if start_date else "  ·  Fecha de inicio: <b>No definida</b>"),
        _style(9, color=DGRAY)
    ))
    story.append(Spacer(1, 0.3*cm))

    # Banner de salud
    salud_data = [[Paragraph(f"<b>{salud_label}</b>",
                             _style(13, bold=True, color=WHITE, align=TA_CENTER))]]
    salud_table = Table(salud_data, colWidths=[W])
    salud_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), salud_color),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), 4),
    ]))
    story.append(salud_table)
    story.append(Spacer(1, 0.4*cm))

    # ── KPIs ──────────────────────────────────────────────────
    kpi_cells = [
        [Paragraph(f"<b>{kpis.completed}</b>", _style(26, bold=True, color=GREEN, align=TA_CENTER)),
         Paragraph(f"<b>{kpis.in_progress}</b>", _style(26, bold=True, color=YELL, align=TA_CENTER)),
         Paragraph(f"<b>{kpis.pending}</b>", _style(26, bold=True, color=NAVY, align=TA_CENTER)),
         Paragraph(f"<b>{kpis.pct_completed:.0f}%</b>", _style(26, bold=True, color=TEAL, align=TA_CENTER))],
        [Paragraph("✅ COMPLETADAS",  _style(8, color=GREEN, align=TA_CENTER)),
         Paragraph("🟡 EN PROGRESO",  _style(8, color=YELL,  align=TA_CENTER)),
         Paragraph("⚪ PENDIENTES",   _style(8, color=NAVY,  align=TA_CENTER)),
         Paragraph("📈 % AVANCE",     _style(8, color=TEAL,  align=TA_CENTER))],
    ]
    kpi_table = Table(kpi_cells, colWidths=[W/4]*4)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), LGRAY),
        ("TOPPADDING",    (0,0), (-1,0),  12),
        ("BOTTOMPADDING", (0,1), (-1,1),  10),
        ("LINEBELOW",     (0,0), (-1,0),  0.5, colors.HexColor("#E2E8F0")),
        ("BOX",           (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID",     (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Avance por fase ───────────────────────────────────────
    story.append(Paragraph("<b>AVANCE POR FASE</b>", _style(11, bold=True, color=NAVY)))
    story.append(Spacer(1, 0.2*cm))

    fase_header = [
        Paragraph("<b>FASE</b>",        _style(9, bold=True, color=WHITE, align=TA_CENTER)),
        Paragraph("<b>NOMBRE</b>",       _style(9, bold=True, color=WHITE, align=TA_LEFT)),
        Paragraph("<b>TOTAL</b>",        _style(9, bold=True, color=WHITE, align=TA_CENTER)),
        Paragraph("<b>COMPLETADAS</b>",  _style(9, bold=True, color=WHITE, align=TA_CENTER)),
        Paragraph("<b>EN PROGRESO</b>",  _style(9, bold=True, color=WHITE, align=TA_CENTER)),
        Paragraph("<b>% AVANCE</b>",     _style(9, bold=True, color=WHITE, align=TA_CENTER)),
    ]
    fase_rows = [fase_header]
    for fn, pd_data in phase_progress.items():
        bg = colors.white if fn % 2 == 0 else LGRAY
        pct = pd_data["pct"]
        pct_color = GREEN if pct >= 80 else (YELL if pct >= 40 else RED)
        fase_rows.append([
            Paragraph(f"<b>F{fn}</b>",         _style(9, bold=True, align=TA_CENTER)),
            Paragraph(pd_data["name"],          _style(9)),
            Paragraph(str(pd_data["total"]),    _style(9, align=TA_CENTER)),
            Paragraph(str(pd_data["completed"]),_style(9, color=GREEN, align=TA_CENTER, bold=True)),
            Paragraph(str(pd_data["in_progress"]),_style(9, color=YELL, align=TA_CENTER)),
            Paragraph(f"<b>{pct}%</b>",         _style(9, bold=True, color=pct_color, align=TA_CENTER)),
        ])

    fase_table = Table(fase_rows, colWidths=[1.2*cm, W*0.42, 1.4*cm, 2.2*cm, 2.2*cm, 1.8*cm])
    ts = [
        ("BACKGROUND",   (0,0), (-1,0),  NAVY),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("BOX",          (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID",    (0,0), (-1,-1), 0.3, colors.HexColor("#E2E8F0")),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]
    for i in range(1, len(fase_rows)):
        if i % 2 == 0:
            ts.append(("BACKGROUND", (0,i), (-1,i), LGRAY))
    fase_table.setStyle(TableStyle(ts))
    story.append(fase_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Actividades atrasadas ─────────────────────────────────
    if atrasadas:
        story.append(HRFlowable(width=W, color=RED, thickness=1))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(
            f"<b>⚠ ACTIVIDADES ATRASADAS ({len(atrasadas)})</b>",
            _style(11, bold=True, color=RED)
        ))
        story.append(Spacer(1, 0.2*cm))

        atr_header = [
            Paragraph("<b>#</b>",             _style(9, bold=True, color=WHITE, align=TA_CENTER)),
            Paragraph("<b>ACTIVIDAD</b>",      _style(9, bold=True, color=WHITE)),
            Paragraph("<b>RESPONSABLE</b>",    _style(9, bold=True, color=WHITE, align=TA_CENTER)),
            Paragraph("<b>DEBIÓ INICIAR</b>",  _style(9, bold=True, color=WHITE, align=TA_CENTER)),
        ]
        atr_rows = [atr_header]
        for a in atrasadas:
            atr_rows.append([
                Paragraph(str(a.activity_number), _style(9, align=TA_CENTER)),
                Paragraph(a.activity_name,         _style(9)),
                Paragraph(a.responsable,           _style(9, align=TA_CENTER)),
                Paragraph(f"Semana {a.week_start}", _style(9, color=RED, align=TA_CENTER, bold=True)),
            ])
        atr_table = Table(atr_rows, colWidths=[1*cm, W*0.52, 2.5*cm, 2.5*cm])
        atr_table.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0),  RED),
            ("TOPPADDING",   (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0), (-1,-1), 5),
            ("LEFTPADDING",  (0,0), (-1,-1), 6),
            ("BOX",          (0,0), (-1,-1), 0.5, RED),
            ("INNERGRID",    (0,0), (-1,-1), 0.3, colors.HexColor("#FEE2E2")),
            ("BACKGROUND",   (0,1), (-1,-1), colors.HexColor("#FFF5F5")),
        ]))
        story.append(atr_table)
        story.append(Spacer(1, 0.3*cm))

    # ── Pie de página ─────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width=W, color=colors.HexColor("#E2E8F0"), thickness=0.5))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        f"Compliance Monitor · Sofgen Pharma · Cumplimiento Legal Corporativo · {today.strftime('%d/%m/%Y')}",
        _style(8, color=DGRAY, align=TA_CENTER)
    ))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
