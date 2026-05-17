from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .config import (
    COUNTRY_ISO3,
    COUNTRY_NAMES,
    DEFAULT_TIMEFRAME,
    GOLD,
    GOLD_SOFT,
    MUTED,
    NAVY,
    NAVY_DARK,
    PALETTE_CATEGORICAL,
    PALETTE_CURRENT,
    PALETTE_PREVIOUS,
    PLOTLY_LAYOUT_DEFAULTS,
    TIMEFRAME_LABELS,
)

MILESTONE_ORDER = ["Kickoff", "Longlist", "Shortlist", "Offer", "Accepted"]
STATUS_COLOURS = {
    "Open": NAVY,
    "On Hold": GOLD,
    "Cancelled": "#B23A48",
    "Closed": "#2E7D5B",
}


def _period_labels(timeframe: str | None) -> tuple[str, str]:
    key = timeframe if timeframe in TIMEFRAME_LABELS else DEFAULT_TIMEFRAME
    _, current, previous = TIMEFRAME_LABELS[key]
    return current.capitalize(), previous.capitalize()


def _empty_figure(message: str = "No data for the selected filters") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        showarrow=False,
        font=dict(size=14, color="#6B7280"),
        xref="paper", yref="paper", x=0.5, y=0.5,
    )
    fig.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def _apply_defaults(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    fig.update_layout(title_text=title)
    fig.update_xaxes(showgrid=False, linecolor="#E5E1D7", ticks="outside")
    fig.update_yaxes(gridcolor="#EFEAE0", zerolinecolor="#EFEAE0")
    return fig


# Row 1: revenue + conversion + status
def revenue_by_country(
    eng: pd.DataFrame,
    min_date: pd.Timestamp,
    prev_min_date: pd.Timestamp,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> go.Figure:

    cur = eng[eng["close_date"] >= min_date].groupby("country")["fee_kEUR"].sum()
    prev = eng[
        (eng["close_date"] < min_date) & (eng["close_date"] >= prev_min_date)
    ].groupby("country")["fee_kEUR"].sum()

    if cur.empty and prev.empty:
        return _empty_figure()

    countries = sorted(set(cur.index) | set(prev.index))
    cur = cur.reindex(countries, fill_value=0)
    prev = prev.reindex(countries, fill_value=0)

    cur_label, prev_label = _period_labels(timeframe)

    fig = go.Figure([
        go.Bar(name=cur_label, x=countries, y=cur.values,
               marker_color=PALETTE_CURRENT,
               text=[f"{v:,.0f}" for v in cur.values],
               textposition="outside", textfont=dict(color=NAVY, size=11),
               cliponaxis=False,
               hovertemplate="<b>%{x}</b><br>%{y:,.0f} kEUR"
                             f"<extra>{cur_label}</extra>"),
        go.Bar(name=prev_label, x=countries, y=prev.values,
               marker_color=PALETTE_PREVIOUS,
               text=[f"{v:,.0f}" for v in prev.values],
               textposition="outside", textfont=dict(color="#8A6A0F", size=11),
               cliponaxis=False,
               hovertemplate="<b>%{x}</b><br>%{y:,.0f} kEUR"
                             f"<extra>{prev_label}</extra>"),
    ])
    fig.update_layout(barmode="group", yaxis_title="Revenue (kEUR)")
    return _apply_defaults(fig, "Revenue by country")


def revenue_world_map(
    eng: pd.DataFrame,
    min_date: pd.Timestamp,
    prev_min_date: pd.Timestamp,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> go.Figure:

    cur = eng[eng["close_date"] >= min_date].groupby("country")["fee_kEUR"].sum()
    prev = eng[
        (eng["close_date"] < min_date) & (eng["close_date"] >= prev_min_date)
    ].groupby("country")["fee_kEUR"].sum()

    if cur.empty and prev.empty:
        return _empty_figure()

    countries = sorted(set(cur.index) | set(prev.index))
    cur = cur.reindex(countries, fill_value=0).round(0)
    prev = prev.reindex(countries, fill_value=0).round(0)

    iso3 = [COUNTRY_ISO3.get(c, c) for c in countries]
    names = [COUNTRY_NAMES.get(c, c) for c in countries]
    delta = (cur.values - prev.values).round(0)

    cur_label, prev_label = _period_labels(timeframe)

    colorscale = [
        [0.0, "#F3EFE3"],
        [0.35, "#9FB4CC"],
        [0.7, "#3F6491"],
        [1.0, NAVY],
    ]

    fig = go.Figure(go.Choropleth(
        locations=iso3,
        locationmode="ISO-3",
        z=cur.values,
        text=names,
        zmin=0,
        colorscale=colorscale,
        marker_line_color="white",
        marker_line_width=0.6,
        colorbar=dict(
            title=dict(
                text=f"{cur_label}<br>(kEUR)",
                font=dict(size=10, color=NAVY),
            ),
            tickfont=dict(size=10, color=MUTED),
            tickformat=",.0f",
            separatethousands=True,
            len=0.7, thickness=10, x=0.99, outlinewidth=0,
        ),
        customdata=list(zip(prev.values, delta)),
        hovertemplate=(
            "<b>%{text}</b><br>"
            f"{cur_label}: %{{z:,.0f}} kEUR<br>"
            f"{prev_label}: %{{customdata[0]:,.0f}} kEUR<br>"
            "Delta: %{customdata[1]:+,.0f} kEUR<extra></extra>"
        ),
        showscale=True,
    ))

    fig.update_geos(
        showcoastlines=False,
        showcountries=True,
        countrycolor="#E5E1D7",
        showland=True,
        landcolor="#FBFAF6",
        showocean=False,
        showlakes=False,
        showframe=False,
        projection_type="natural earth",
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    fig.update_layout(
        title_text="Revenue by country - cohort map",
        margin=dict(l=10, r=10, t=60, b=10),
        showlegend=False,
        geo=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def conversion_funnel(
    eng: pd.DataFrame, milestones: pd.DataFrame, min_date: pd.Timestamp
) -> go.Figure:
    ids = eng[eng["close_date"] >= min_date]["engagement_id"]
    df = milestones[milestones["engagement_id"].isin(ids)]
    if df.empty:
        return _empty_figure()

    counts = df.groupby("milestone")["candidate_count"].mean().apply(lambda x: round(x, 1))
    counts = counts.reindex(MILESTONE_ORDER).dropna()
    if counts.empty:
        return _empty_figure()

    base = counts.iloc[0] or 1
    pct = (counts / base * 100).round(0).astype(int)

    fig = go.Figure(go.Funnel(
        y=counts.index,
        x=counts.values,
        textinfo="value+percent initial",
        marker=dict(color=[NAVY, "#27466F", "#3F6491", GOLD, "#C98A1A"]),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} candidates<extra></extra>",
        customdata=pct,
    ))
    fig.update_layout(showlegend=False)
    return _apply_defaults(fig, "Candidate conversion funnel")


def status_breakdown(eng: pd.DataFrame) -> go.Figure:
    df = eng[(eng["close_date"].isna()) & (eng["status"] != "Closed")]
    counts = df["status"].value_counts()
    if counts.empty:
        return _empty_figure("All engagements are closed for this slice")

    colours = [STATUS_COLOURS.get(s, NAVY) for s in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.55,
        marker=dict(colors=colours, line=dict(color="white", width=2)),
        textinfo="percent", textfont=dict(color="white", size=13),
        hovertemplate="<b>%{label}</b><br>%{value} engagements"
                      " (%{percent})<extra></extra>",
    ))
    fig.update_layout(showlegend=True)
    return _apply_defaults(fig, "Status of active engagements")


# Row 2: revenue trend + average milestone duration
def revenue_time_series(
    eng: pd.DataFrame,
    min_date: pd.Timestamp,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> go.Figure:

    df = eng[eng["close_date"] >= min_date][["close_date", "fee_kEUR"]].copy()
    if df.empty:
        return _empty_figure()

    df = df.set_index("close_date").sort_index()
    rule = "W" if timeframe == "month" else "MS"
    series = df["fee_kEUR"].resample(rule).sum()
    if series.empty or series.sum() == 0:
        return _empty_figure()

    cur_label, _ = _period_labels(timeframe)

    fig = go.Figure(go.Scatter(
        x=series.index, y=series.values,
        mode="lines+markers",
        name=cur_label,
        line=dict(color=NAVY, width=2.5),
        marker=dict(color=GOLD, size=8,
                    line=dict(color=NAVY, width=1.5)),
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>%{y:,.0f} kEUR<extra></extra>",
    ))
    fig.update_layout(yaxis_title="Revenue (kEUR)", showlegend=False)
    return _apply_defaults(fig, "Revenue trend")


def milestone_avg_time(
    eng: pd.DataFrame, milestones: pd.DataFrame, min_date: pd.Timestamp
) -> go.Figure:

    ids = eng[eng["close_date"] >= min_date]["engagement_id"]
    df = milestones[milestones["engagement_id"].isin(ids)]
    if df.empty:
        return _empty_figure()

    pivot = (
        df.pivot_table(
            index="engagement_id",
            columns="milestone",
            values="milestone_date",
            aggfunc="first",
        )
        .reindex(columns=MILESTONE_ORDER)
    )
    if pivot.empty:
        return _empty_figure()

    diffs = pivot.diff(axis=1).iloc[:, 1:]
    avg_days = diffs.mean().dt.days
    avg_days = avg_days.dropna()
    if avg_days.empty:
        return _empty_figure()

    labels = [
        f"{MILESTONE_ORDER[i - 1]} -> {MILESTONE_ORDER[i]}"
        for i in range(1, len(MILESTONE_ORDER))
        if MILESTONE_ORDER[i] in avg_days.index
    ]
    values = [int(avg_days[MILESTONE_ORDER[i]])
              for i in range(1, len(MILESTONE_ORDER))
              if MILESTONE_ORDER[i] in avg_days.index]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=PALETTE_CURRENT,
        text=[f"{v} d" for v in values],
        textposition="outside", textfont=dict(color=NAVY, size=11),
        cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>%{y} days<extra></extra>",
    ))
    fig.update_layout(yaxis_title="Days", showlegend=False)
    return _apply_defaults(fig, "Average time between milestones")


# Row 3: distributions and partner ranking
def _grouped_count_chart(
    eng: pd.DataFrame,
    column: str,
    min_date: pd.Timestamp,
    prev_min_date: pd.Timestamp,
    title: str,
    category_order: list[str] | None = None,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> go.Figure:
    cur = eng[eng["close_date"] >= min_date][column].value_counts()
    prev = eng[
        (eng["close_date"] < min_date) & (eng["close_date"] >= prev_min_date)
    ][column].value_counts()

    if cur.empty and prev.empty:
        return _empty_figure()

    cats = category_order or sorted(set(cur.index) | set(prev.index))
    cur = cur.reindex(cats, fill_value=0)
    prev = prev.reindex(cats, fill_value=0)

    cur_label, prev_label = _period_labels(timeframe)

    fig = go.Figure([
        go.Bar(name=cur_label, x=cats, y=cur.values,
               marker_color=PALETTE_CURRENT,
               text=[str(int(v)) for v in cur.values],
               textposition="outside", textfont=dict(color=NAVY, size=11),
               cliponaxis=False,
               hovertemplate="<b>%{x}</b><br>%{y} engagements"
                             f"<extra>{cur_label}</extra>"),
        go.Bar(name=prev_label, x=cats, y=prev.values,
               marker_color=PALETTE_PREVIOUS,
               text=[str(int(v)) for v in prev.values],
               textposition="outside", textfont=dict(color="#8A6A0F", size=11),
               cliponaxis=False,
               hovertemplate="<b>%{x}</b><br>%{y} engagements"
                             f"<extra>{prev_label}</extra>"),
    ])
    fig.update_layout(barmode="group", yaxis_title="Engagements")
    return _apply_defaults(fig, title)


def level_distribution(
    eng: pd.DataFrame,
    min_date: pd.Timestamp,
    prev_min_date: pd.Timestamp,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> go.Figure:
    return _grouped_count_chart(
        eng, "level", min_date, prev_min_date,
        "Engagements by level",
        category_order=["Board", "CxO", "VP"],
        timeframe=timeframe,
    )


def size_distribution(
    eng: pd.DataFrame,
    min_date: pd.Timestamp,
    prev_min_date: pd.Timestamp,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> go.Figure:
    return _grouped_count_chart(
        eng, "client_size", min_date, prev_min_date,
        "Engagements by client size",
        category_order=["Small", "Medium", "Large"],
        timeframe=timeframe,
    )


def lead_partner_ranking(
    eng: pd.DataFrame,
    min_date: pd.Timestamp,
    prev_min_date: pd.Timestamp,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> go.Figure:
    cur = eng[eng["close_date"] >= min_date]["lead_partner"].value_counts()
    prev = eng[
        (eng["close_date"] < min_date) & (eng["close_date"] >= prev_min_date)
    ]["lead_partner"].value_counts()
    if cur.empty and prev.empty:
        return _empty_figure()

    partners = sorted(set(cur.index.dropna()) | set(prev.index.dropna()))
    cur = cur.reindex(partners, fill_value=0)
    prev = prev.reindex(partners, fill_value=0)

    cur_label, prev_label = _period_labels(timeframe)

    fig = go.Figure([
        go.Bar(name=cur_label, y=partners, x=cur.values, orientation="h",
               marker_color=PALETTE_CURRENT,
               text=[str(int(v)) for v in cur.values],
               textposition="outside", textfont=dict(color=NAVY, size=11),
               cliponaxis=False,
               hovertemplate="<b>%{y}</b><br>%{x} closed"
                             f"<extra>{cur_label}</extra>"),
        go.Bar(name=prev_label, y=partners, x=prev.values, orientation="h",
               marker_color=PALETTE_PREVIOUS,
               text=[str(int(v)) for v in prev.values],
               textposition="outside", textfont=dict(color="#8A6A0F", size=11),
               cliponaxis=False,
               hovertemplate="<b>%{y}</b><br>%{x} closed"
                             f"<extra>{prev_label}</extra>"),
    ])
    fig.update_layout(barmode="group", xaxis_title="Closed engagements")
    return _apply_defaults(fig, "Closed engagements by lead partner")
