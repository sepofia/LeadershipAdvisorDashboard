from __future__ import annotations

from datetime import date
from typing import List, Sequence

import dash_bootstrap_components as dbc
from dash import dcc, html

from .config import (
    DASHBOARD_TAGLINE,
    DEFAULT_TIMEFRAME,
    LOGO_URL,
    TIMEFRAME_OPTIONS,
)
from .metrics import KpiValue


# Header / navbar
def make_navbar(report_date: date) -> dbc.Navbar:
    brand = html.Div(
        [
            html.Img(src=LOGO_URL, className="ss-logo"),
            ],
        className="ss-brand",
    )

    timeframe = html.Div(
        [
            html.Span("Timeframe", className="ss-timeframe-label"),
            dbc.RadioItems(
                id="select-time",
                className="ss-timeframe",
                inputClassName="btn-check",
                labelClassName="btn ss-timeframe-btn",
                labelCheckedClassName="active",
                options=TIMEFRAME_OPTIONS,
                value=DEFAULT_TIMEFRAME,
                inline=True,
            ),
        ],
        className="ss-timeframe-wrap",
    )

    meta = html.Div(
        [
            html.Div("Report generated", className="ss-meta-label"),
            html.Div(report_date.strftime("%B %d, %Y"), className="ss-meta-date"),
        ],
        className="ss-meta",
    )

    return dbc.Navbar(
        dbc.Container(
            [brand, timeframe, meta],
            className="ss-navbar-inner",
            fluid=True,
        ),
        className="ss-navbar",
        color="transparent",
        dark=True,
    )


# Tagline strip
def make_tagline() -> html.Section:
    return html.Section(
        dbc.Container(
            [
                html.Div(
                    [
                        html.Span("Take-home Exersice", className="ss-tagline-eyebrow"),
                        html.H1(DASHBOARD_TAGLINE, className="ss-tagline-title"),
                    ],
                    className="ss-tagline-text",
                ),
            ],
            fluid=True,
            className="ss-tagline-inner",
        ),
        className="ss-tagline",
    )


# Filter card (region + industry + data-quality popover trigger)
NOTES_TRIGGER_ID = "ss-notes-trigger"
NOTES_POPOVER_ID = "ss-notes-popover"


def _format_ids(ids: List[str], max_visible: int = 12) -> str:
    if not ids:
        return "None"
    if len(ids) <= max_visible:
        return ", ".join(ids)
    return ", ".join(ids[:max_visible]) + f" (+{len(ids) - max_visible} more)"


def _notes_items(
    wrong_closed: List[str],
    missed_closed_data: List[str],
    missed_lead: List[str],
):
    return [
        (
            "Status mismatch",
            "Engagements marked Open with a close date have been excluded from analytics.",
            wrong_closed,
            "ss-note-warning",
        ),
        (
            "Missing close date",
            "Engagements marked Closed but lacking a close date; metrics may understate volume.",
            missed_closed_data,
            "ss-note-warning",
        ),
        (
            "Lead partner not assigned",
            "Engagements without an assigned lead partner; ownership review recommended.",
            missed_lead,
            "ss-note-info",
        ),
    ]


def _make_notes_trigger(active_count: int, total: int) -> html.Div:

    if active_count == 0:
        summary = "No warnings"
        modifier = "ss-trigger-clean"
        icon = "\u2713"
    else:
        plural = "s" if active_count != 1 else ""
        summary = f"{active_count} warning{plural}"
        modifier = "ss-trigger-warn"
        icon = "\u26A0"

    return html.Div(
        [
            html.Span(icon, className="ss-trigger-icon"),
            html.Span(summary, className="ss-trigger-text"),
            html.Span(f"{total} items", className="ss-trigger-count"),
        ],
        id=NOTES_TRIGGER_ID,
        className=f"ss-notes-trigger {modifier}",
        tabIndex=0,
    )


def _make_notes_popover(
    wrong_closed: List[str],
    missed_closed_data: List[str],
    missed_lead: List[str],
) -> dbc.Popover:
    rows = []
    for title, text, ids, modifier in _notes_items(
        wrong_closed, missed_closed_data, missed_lead
    ):
        rows.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(title, className="ss-note-title"),
                            html.Span(f"{len(ids)}", className="ss-note-count"),
                        ],
                        className="ss-note-head",
                    ),
                    html.Div(text, className="ss-note-text"),
                    html.Div(_format_ids(ids), className="ss-note-ids"),
                ],
                className=f"ss-note {modifier}",
            )
        )

    body = dbc.PopoverBody(
        [
            html.Div(
                [
                    html.Span("Data quality", className="ss-section-eyebrow"),
                    html.H4(
                        "Items requiring attention",
                        className="ss-section-title",
                    ),
                ],
                className="ss-section-header",
            ),
            html.Div(rows, className="ss-notes-grid"),
        ],
        className="ss-notes-popover-body",
    )

    return dbc.Popover(
        body,
        id=NOTES_POPOVER_ID,
        target=NOTES_TRIGGER_ID,
        trigger="hover focus",
        placement="bottom",
        hide_arrow=False,
        className="ss-notes-popover",
    )


def make_filter_bar(
    regions: Sequence[str],
    practices: Sequence[str],
    wrong_closed: List[str],
    missed_closed_data: List[str],
    missed_lead: List[str],
) -> dbc.Card:
    region_options = [{"label": "All regions", "value": "all"}] + [
        {"label": r, "value": r} for r in regions
    ]
    practice_options = [{"label": "All industries", "value": "all"}] + [
        {"label": p, "value": p} for p in practices
    ]

    active_count = sum(
        1 for ids in (wrong_closed, missed_closed_data, missed_lead) if ids
    )
    total = len(wrong_closed) + len(missed_closed_data) + len(missed_lead)

    trigger = _make_notes_trigger(active_count, total)
    popover = _make_notes_popover(wrong_closed, missed_closed_data, missed_lead)

    download_col = dbc.Col(
        [
            html.Label("Export", className="ss-filter-label"),
            dbc.Button(
                [
                    html.I(className="bi bi-download me-2"),
                    "Download PDF",
                ],
                id="btn-pdf",
                n_clicks=0,
                className="ss-pdf-btn",
            ),
        ],
        md=2,
    )

    return dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Region", className="ss-filter-label"),
                            dcc.Dropdown(
                                id="dropdown-region",
                                options=region_options,
                                value="all",
                                clearable=False,
                                className="ss-dropdown",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Industry", className="ss-filter-label"),
                            dcc.Dropdown(
                                id="dropdown-practice",
                                options=practice_options,
                                value="all",
                                clearable=False,
                                className="ss-dropdown",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Data quality", className="ss-filter-label"),
                            trigger,
                            popover,
                        ],
                        md=4,
                    ),
                    download_col,
                ],
                className="g-3 align-items-end",
            ),
        ),
        className="ss-card ss-filter-card",
    )


# KPI cards
def render_kpi_card(kpi: KpiValue) -> dbc.Card:
    direction = "up" if kpi.delta >= 0 else "down"
    sentiment = "positive" if (kpi.delta >= 0) == kpi.positive_is_good else "negative"
    if kpi.delta == 0:
        sentiment = "neutral"
    arrow = "\u25B2" if direction == "up" else "\u25BC"
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(kpi.title, className="ss-kpi-title"),
                html.Div(kpi.value, className="ss-kpi-value"),
                html.Div(
                    [
                        html.Span(arrow, className="ss-kpi-arrow"),
                        html.Span(kpi.delta_label, className="ss-kpi-delta-text"),
                        html.Span(" vs previous", className="ss-kpi-delta-period"),
                    ],
                    className=f"ss-kpi-delta ss-kpi-{sentiment}",
                ),
            ]
        ),
        className="ss-card ss-kpi-card",
    )


def make_kpi_row() -> dbc.Row:
    cols = []
    for kid in [
        "revenue-card",
        "eng-opened-card",
        "eng-closed-card",
        "eng-cancelled-card",
        "avg-time-card",
        "acc-rate-card",
    ]:
        cols.append(dbc.Col(html.Div(id=kid), xs=12, sm=6, md=4, lg=2))
    return dbc.Row(cols, className="g-3 ss-kpi-row")


# Chart cards
def make_chart_card(chart_id: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            dcc.Loading(
                dcc.Graph(id=chart_id, config={"displayModeBar": False}),
                type="dot",
                color="#163056",
            )
        ),
        className="ss-card ss-chart-card",
    )


def make_charts_section() -> html.Div:
    row1 = dbc.Row(
        [
            dbc.Col(make_chart_card("chart-revenue"), lg=5, md=12),
            dbc.Col(make_chart_card("chart-funnel"), lg=4, md=12),
            dbc.Col(make_chart_card("chart-status"), lg=3, md=12),
        ],
        className="g-3",
    )
    row2 = dbc.Row(
        [
            dbc.Col(make_chart_card("chart-time-series"), lg=6, md=12),
            dbc.Col(make_chart_card("chart-time-diff"), lg=6, md=12),
        ],
        className="g-3 mt-1",
    )
    row3 = dbc.Row(
        [
            dbc.Col(make_chart_card("chart-level"), lg=4, md=12),
            dbc.Col(make_chart_card("chart-size"), lg=4, md=12),
            dbc.Col(make_chart_card("chart-lead"), lg=4, md=12),
        ],
        className="g-3 mt-1",
    )
    return html.Div(
        [
            html.Div(
                [
                    html.Span("Performance", className="ss-section-eyebrow"),
                    html.H4("Engagements overview", className="ss-section-title"),
                ],
                className="ss-section-header",
            ),
            row1,
            row2,
            row3,
        ],
        className="ss-charts",
    )


# Footer
def make_footer() -> html.Footer:
    year = date.today().year
    return html.Footer(
        dbc.Container(
            [
                html.Span(f"\u00A9 {year} Spencer Stuart", className="ss-footer-left"),
                html.Span(
                    "Prepared by Sofiia Shishkina",
                    className="ss-footer-right",
                ),
            ],
            fluid=True,
            className="ss-footer-inner",
        ),
        className="ss-footer",
    )


# Full page assembly
def make_layout(
    regions: Sequence[str],
    practices: Sequence[str],
    report_date: date,
    wrong_closed: List[str],
    missed_closed_data: List[str],
    missed_lead: List[str],
) -> html.Div:
    filter_bar = make_filter_bar(
        regions, practices, wrong_closed, missed_closed_data, missed_lead
    )
    return html.Div(
        [
            dcc.Download(id="pdf-download"),
            make_navbar(report_date),
            make_tagline(),
            dbc.Container(
                [
                    dbc.Row(
                        dbc.Col(filter_bar, width=12),
                        className="g-3 ss-top-row",
                    ),
                    make_kpi_row(),
                    make_charts_section(),
                ],
                fluid=True,
                className="ss-content",
            ),
            make_footer(),
        ],
        className="ss-app",
    )
