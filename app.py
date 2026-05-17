from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc

from src import charts
from src.config import DASHBOARD_TITLE, USE_REVENUE_WORLD_MAP
from src.data_processing import (
    Dataset,
    filter_engagements,
    load_dataset,
    timeframe_bounds,
)
from src.layout import make_layout, render_kpi_card
from src.metrics import compute_kpis
from src.pdf_report import build_pdf


def build_app(data: Dataset) -> dash.Dash:
    external_stylesheets = [
        dbc.themes.FLATLY,
        dbc.icons.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700"
        "&family=Lora:ital,wght@0,500;0,600;1,500&display=swap",
    ]
    app = dash.Dash(
        __name__,
        external_stylesheets=external_stylesheets,
        title=f"{DASHBOARD_TITLE} - Spencer Stuart",
        suppress_callback_exceptions=True,
    )

    app.layout = make_layout(
        regions=data.regions,
        practices=data.practices,
        report_date=data.report_date,
        wrong_closed=data.wrong_closed,
        missed_closed_data=data.missed_closed_data,
        missed_lead=data.missed_lead,
    )

    _register_callbacks(app, data)
    return app


def _register_callbacks(app: dash.Dash, data: Dataset) -> None:
    @app.callback(
        Output("revenue-card", "children"),
        Output("eng-opened-card", "children"),
        Output("eng-closed-card", "children"),
        Output("eng-cancelled-card", "children"),
        Output("avg-time-card", "children"),
        Output("acc-rate-card", "children"),
        Output("chart-revenue", "figure"),
        Output("chart-funnel", "figure"),
        Output("chart-status", "figure"),
        Output("chart-time-series", "figure"),
        Output("chart-time-diff", "figure"),
        Output("chart-level", "figure"),
        Output("chart-size", "figure"),
        Output("chart-lead", "figure"),
        Input("select-time", "value"),
        Input("dropdown-region", "value"),
        Input("dropdown-practice", "value"),
    )
    def _update(timeframe, region, practice):
        engagements = filter_engagements(data.engagements, region, practice)
        min_date, prev_min_date = timeframe_bounds(data.max_date, timeframe)

        kpis = compute_kpis(engagements, min_date, prev_min_date)
        kpi_cards = [render_kpi_card(k) for k in kpis]

        revenue_fig = (
            charts.revenue_world_map(
                engagements, min_date, prev_min_date, timeframe
            )
            if USE_REVENUE_WORLD_MAP
            else charts.revenue_by_country(
                engagements, min_date, prev_min_date, timeframe
            )
        )
        figures = [
            revenue_fig,
            charts.conversion_funnel(engagements, data.milestones, min_date),
            charts.status_breakdown(engagements),
            charts.revenue_time_series(engagements, min_date, timeframe),
            charts.milestone_avg_time(engagements, data.milestones, min_date),
            charts.level_distribution(
                engagements, min_date, prev_min_date, timeframe
            ),
            charts.size_distribution(
                engagements, min_date, prev_min_date, timeframe
            ),
            charts.lead_partner_ranking(
                engagements, min_date, prev_min_date, timeframe
            ),
        ]

        return (*kpi_cards, *figures)

    @app.callback(
        Output("pdf-download", "data"),
        Input("btn-pdf", "n_clicks"),
        State("select-time", "value"),
        State("dropdown-region", "value"),
        State("dropdown-practice", "value"),
        prevent_initial_call=True,
    )
    def _download_pdf(_n_clicks, timeframe, region, practice):
        pdf_bytes = build_pdf(data, timeframe, region, practice)
        region_slug = (region or "all").lower().replace(" ", "-")
        practice_slug = (practice or "all").lower().replace(" ", "-")
        fname = (
            f"spencer_stuart_report_{timeframe}_"
            f"{region_slug}_{practice_slug}.pdf"
        )
        return dcc.send_bytes(pdf_bytes, filename=fname)


dataset = load_dataset()
app = build_app(dataset)
server = app.server


if __name__ == "__main__":
    app.run()
