from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass(frozen=True)
class KpiValue:

    title: str
    value: str                      # already formatted for display
    delta: float                    # signed change vs the previous period
    delta_label: str                # already formatted for display, e.g. "+12 kEUR"
    positive_is_good: bool = True


def _format_currency(amount: float) -> str:
    return f"{round(amount):,} kEUR".replace(",", " ")


def _format_int(amount: float) -> str:
    return f"{int(round(amount)):,}".replace(",", " ")


def _format_rate(value: float) -> str:
    return f"{value * 100:.0f}%"


def _delta_str(value: float, suffix: str = "", as_int: bool = False) -> str:
    sign = "+" if value >= 0 else "-"
    abs_value = abs(value)
    if as_int:
        body = f"{int(round(abs_value)):,}".replace(",", " ")
    else:
        body = f"{abs_value:,.1f}".rstrip("0").rstrip(".").replace(",", " ")
    return f"{sign}{body}{suffix}"


def compute_kpis(
    engagements: pd.DataFrame,
    min_date: pd.Timestamp,
    prev_min_date: pd.Timestamp,
) -> List[KpiValue]:

    closed_cur = engagements[engagements["close_date"] >= min_date]
    closed_prev = engagements[
        (engagements["close_date"] < min_date)
        & (engagements["close_date"] >= prev_min_date)
    ]

    # ---- Revenue (sum of fees on engagements closed in window) -----------
    revenue_cur = closed_cur["fee_kEUR"].sum()
    revenue_prev = closed_prev["fee_kEUR"].sum()

    # ---- Engagement counts ----------------------------------------------
    opened_cur = engagements[engagements["start_date"] >= min_date].shape[0]
    opened_prev = engagements[
        (engagements["start_date"] < min_date)
        & (engagements["start_date"] >= prev_min_date)
    ].shape[0]
    closed_count_cur = closed_cur[closed_cur["status"] == "Closed"].shape[0]
    closed_count_prev = closed_prev[closed_prev["status"] == "Closed"].shape[0]
    cancelled_cur = closed_cur[closed_cur["status"] == "Cancelled"].shape[0]
    cancelled_prev = closed_prev[closed_prev["status"] == "Cancelled"].shape[0]

    # ---- Average closing time -------------------------------------------
    def _avg_days(df):
        only_closed = df[df["status"] == "Closed"]
        if only_closed.empty:
            return 0.0
        return (only_closed["close_date"] - only_closed["start_date"]).dt.days.mean()

    avg_cur = _avg_days(closed_cur)
    avg_prev = _avg_days(closed_prev)

    # ---- Completion rate -------------------------------------------------
    def _rate(closed_n, cancelled_n):
        denom = closed_n + cancelled_n
        return closed_n / denom if denom else 0.0

    rate_cur = _rate(closed_count_cur, cancelled_cur)
    rate_prev = _rate(closed_count_prev, cancelled_prev)

    return [
        KpiValue(
            "Revenue",
            _format_currency(revenue_cur),
            revenue_cur - revenue_prev,
            _delta_str(revenue_cur - revenue_prev, " kEUR", as_int=True),
        ),
        KpiValue(
            "Engagements opened",
            _format_int(opened_cur),
            opened_cur - opened_prev,
            _delta_str(opened_cur - opened_prev, as_int=True),
        ),
        KpiValue(
            "Engagements closed",
            _format_int(closed_count_cur),
            closed_count_cur - closed_count_prev,
            _delta_str(closed_count_cur - closed_count_prev, as_int=True),
        ),
        KpiValue(
            "Engagements cancelled",
            _format_int(cancelled_cur),
            cancelled_cur - cancelled_prev,
            _delta_str(cancelled_cur - cancelled_prev, as_int=True),
            positive_is_good=False,
        ),
        KpiValue(
            "Avg. time to close",
            f"{int(round(avg_cur))} d" if avg_cur else "n/a",
            avg_cur - avg_prev,
            _delta_str(avg_cur - avg_prev, " d", as_int=True),
            positive_is_good=False,
        ),
        KpiValue(
            "Completion rate",
            _format_rate(rate_cur),
            rate_cur - rate_prev,
            _delta_str((rate_cur - rate_prev) * 100, " pp", as_int=True),
        ),
    ]
