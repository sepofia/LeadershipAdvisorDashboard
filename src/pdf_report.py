from __future__ import annotations

from datetime import date
from io import BytesIO
from typing import List, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from . import charts
from .config import (
    BORDER,
    DASHBOARD_TITLE,
    GOLD,
    MUTED,
    NAVY,
    SUCCESS,
    DANGER,
    TIMEFRAME_LABELS,
    USE_REVENUE_WORLD_MAP,
    WHITE,
)
from .data_processing import Dataset, filter_engagements, timeframe_bounds
from .metrics import KpiValue, compute_kpis


# Layout constants (A4 landscape, 30 pt margins)
PAGE_W, PAGE_H = landscape(A4)
MARGIN = 30
CHART_PNG_W = 900
CHART_PNG_H = 600
CHART_CELL_W = (PAGE_W - 2 * MARGIN) / 4 - 4
CHART_CELL_H = CHART_CELL_W * CHART_PNG_H / CHART_PNG_W


def _hex(color: str) -> colors.HexColor:
    return colors.HexColor(color)


# Paragraph styles
_EYEBROW = ParagraphStyle(
    "eyebrow", fontName="Helvetica-Bold", fontSize=8, leading=10,
    textColor=_hex(GOLD), spaceAfter=2,
)
_TITLE = ParagraphStyle(
    "title", fontName="Times-Bold", fontSize=20, leading=24,
    textColor=_hex(NAVY), spaceAfter=2,
)
_SUBTITLE = ParagraphStyle(
    "subtitle", fontName="Helvetica", fontSize=10, leading=13,
    textColor=_hex(MUTED),
)
_KPI_LABEL = ParagraphStyle(
    "kpi-label", fontName="Helvetica-Bold", fontSize=7, leading=9,
    textColor=_hex(MUTED), alignment=0,
)
_KPI_VALUE = ParagraphStyle(
    "kpi-value", fontName="Times-Bold", fontSize=16, leading=18,
    textColor=_hex(NAVY),
)
_KPI_DELTA_BASE = dict(fontName="Helvetica-Bold", fontSize=8, leading=10)


# Helpers
def _filter_summary(region: str, practice: str, timeframe: str) -> str:
    tf_label = TIMEFRAME_LABELS.get(timeframe, (timeframe,))[0].capitalize()
    region_label = "All regions" if not region or region == "all" else region
    practice_label = (
        "All industries" if not practice or practice == "all" else practice
    )
    return f"{tf_label}  &middot;  {region_label}  &middot;  {practice_label}"


def _delta_style(kpi: KpiValue) -> ParagraphStyle:
    if kpi.delta == 0:
        color = MUTED
    elif (kpi.delta >= 0) == kpi.positive_is_good:
        color = SUCCESS
    else:
        color = DANGER
    return ParagraphStyle("delta", textColor=_hex(color), **_KPI_DELTA_BASE)


def _kpi_cell(kpi: KpiValue) -> List:
    arrow = "+" if kpi.delta >= 0 else "-"
    delta_text = kpi.delta_label.lstrip("+-")
    return [
        Paragraph(kpi.title.upper(), _KPI_LABEL),
        Spacer(1, 4),
        Paragraph(kpi.value, _KPI_VALUE),
        Spacer(1, 2),
        Paragraph(
            f"{arrow} {delta_text} <font color='{MUTED}'>vs previous</font>",
            _delta_style(kpi),
        ),
    ]


def _figure_to_png(fig) -> bytes:
    # Render a Plotly figure to PNG bytes using Kaleido
    return fig.to_image(
        format="png", width=CHART_PNG_W, height=CHART_PNG_H, scale=2,
    )


def _figure_to_image(fig, width: float, height: float) -> Image:
    img = Image(BytesIO(_figure_to_png(fig)), width=width, height=height)
    img.hAlign = "CENTER"
    return img


# Section builders
def _build_header(timeframe: str, region: str, practice: str, report_date: date):
    table = Table(
        [[
            Paragraph("PERFORMANCE REPORT", _EYEBROW),
            Paragraph(
                f"<font color='{MUTED}'>Generated</font> "
                f"<font color='{NAVY}'><b>{report_date.strftime('%B %d, %Y')}</b></font>",
                _SUBTITLE,
            ),
        ], [
            Paragraph(DASHBOARD_TITLE, _TITLE),
            Paragraph(_filter_summary(region, practice, timeframe), _SUBTITLE),
        ]],
        colWidths=[(PAGE_W - 2 * MARGIN) * 0.6, (PAGE_W - 2 * MARGIN) * 0.4],
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEBELOW", (0, 1), (-1, 1), 2, _hex(GOLD)),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
    ]))
    return table


def _build_kpi_strip(kpis: Sequence[KpiValue]) -> Table:
    cells = [[_kpi_cell(k) for k in kpis]]
    col_w = (PAGE_W - 2 * MARGIN) / len(kpis)
    table = Table(cells, colWidths=[col_w] * len(kpis), rowHeights=[68])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), _hex(WHITE)),
        ("BOX", (0, 0), (-1, -1), 0.5, _hex(BORDER)),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, _hex(BORDER)),
        ("LINEABOVE", (0, 0), (-1, 0), 2, _hex(NAVY)),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return table


def _build_chart_grid(figs: Sequence) -> Table:
    images = [_figure_to_image(f, CHART_CELL_W - 8, CHART_CELL_H - 8) for f in figs]
    rows = [images[:4], images[4:]]
    table = Table(
        rows,
        colWidths=[CHART_CELL_W] * 4,
        rowHeights=[CHART_CELL_H] * 2,
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 0), (-1, -1), _hex(WHITE)),
        ("BOX", (0, 0), (-1, -1), 0.5, _hex(BORDER)),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, _hex(BORDER)),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def build_pdf(
    dataset: Dataset, timeframe: str, region: str, practice: str
) -> bytes:

    engagements = filter_engagements(dataset.engagements, region, practice)
    min_date, prev_min_date = timeframe_bounds(dataset.max_date, timeframe)

    kpis = compute_kpis(engagements, min_date, prev_min_date)

    revenue_fig = (
        charts.revenue_world_map(engagements, min_date, prev_min_date, timeframe)
        if USE_REVENUE_WORLD_MAP
        else charts.revenue_by_country(
            engagements, min_date, prev_min_date, timeframe
        )
    )
    figs = [
        revenue_fig,
        charts.revenue_time_series(engagements, min_date, timeframe),
        charts.milestone_avg_time(engagements, dataset.milestones, min_date),
        charts.conversion_funnel(engagements, dataset.milestones, min_date),
        charts.status_breakdown(engagements),
        charts.level_distribution(engagements, min_date, prev_min_date, timeframe),
        charts.size_distribution(engagements, min_date, prev_min_date, timeframe),
        charts.lead_partner_ranking(
            engagements, min_date, prev_min_date, timeframe
        ),
    ]

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=DASHBOARD_TITLE,
        author="Spencer Stuart",
    )
    story = [
        _build_header(timeframe, region, practice, dataset.report_date),
        Spacer(1, 10),
        _build_kpi_strip(kpis),
        Spacer(1, 10),
        _build_chart_grid(figs),
    ]
    doc.build(story)
    return buffer.getvalue()
