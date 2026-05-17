from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List

import pandas as pd

from .config import ENGAGEMENTS_CSV, MILESTONES_CSV


# Public data container
@dataclass(frozen=True)
class Dataset:

    engagements: pd.DataFrame
    milestones: pd.DataFrame
    max_date: pd.Timestamp
    report_date: date
    wrong_closed: List[str] = field(default_factory=list)
    missed_closed_data: List[str] = field(default_factory=list)
    missed_lead: List[str] = field(default_factory=list)

    @property
    def regions(self) -> List[str]:
        return sorted(self.engagements["region"].dropna().unique().tolist())

    @property
    def practices(self) -> List[str]:
        return sorted(self.engagements["practice"].dropna().unique().tolist())


# Loading helpers
def _read_csv_with_dates(path, date_columns):
    df = pd.read_csv(path)
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _detect_quality_issues(engagements: pd.DataFrame):
    wrong_closed = engagements.loc[
        (engagements["status"] == "Open") & engagements["close_date"].notna(),
        "engagement_id",
    ].tolist()
    missed_closed_data = engagements.loc[
        (engagements["status"] == "Closed") & engagements["close_date"].isna(),
        "engagement_id",
    ].tolist()
    missed_lead = engagements.loc[
        engagements["lead_partner"].isna(), "engagement_id"
    ].tolist()
    return wrong_closed, missed_closed_data, missed_lead


def load_dataset(
    engagements_path=ENGAGEMENTS_CSV, milestones_path=MILESTONES_CSV
) -> Dataset:

    engagements_raw = _read_csv_with_dates(
        engagements_path, ["start_date", "close_date"]
    )
    milestones_raw = _read_csv_with_dates(milestones_path, ["milestone_date"])

    wrong_closed, missed_closed_data, missed_lead = _detect_quality_issues(
        engagements_raw
    )

    # filtration (drop opened engagements with close_date)
    engagements = engagements_raw[
        ~engagements_raw["engagement_id"].isin(wrong_closed)
    ].copy()
    milestones = milestones_raw[
        ~milestones_raw["engagement_id"].isin(wrong_closed)
    ].copy()

    max_date = pd.to_datetime(
        max(engagements["start_date"].max(), engagements["close_date"].max())
    )

    return Dataset(
        engagements=engagements,
        milestones=milestones,
        max_date=max_date,
        report_date=date.today(),
        wrong_closed=wrong_closed,
        missed_closed_data=missed_closed_data,
        missed_lead=missed_lead,
    )


def filter_engagements(
    engagements: pd.DataFrame, region: str | None, practice: str | None
) -> pd.DataFrame:

    df = engagements
    if region and region != "all":
        df = df[df["region"] == region]
    if practice and practice != "all":
        df = df[df["practice"] == practice]
    return df


def timeframe_bounds(max_date: pd.Timestamp, timeframe: str):

    if timeframe == "week":
        return max_date - pd.DateOffset(weeks=1), max_date - pd.DateOffset(weeks=2)
    if timeframe == "month":
        return max_date - pd.DateOffset(months=1), max_date - pd.DateOffset(months=2)
    if timeframe == "quarter":
        return max_date - pd.DateOffset(months=3), max_date - pd.DateOffset(months=6)
    if timeframe == "year":
        return max_date - pd.DateOffset(years=1), max_date - pd.DateOffset(years=2)
    raise RuntimeError("Wrong timeframe")
