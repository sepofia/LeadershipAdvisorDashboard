from pathlib import Path


# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ENGAGEMENTS_CSV = DATA_DIR / "engagements.csv"
MILESTONES_CSV = DATA_DIR / "milestones.csv"

# Brand palette
NAVY = "#163056"            # Spencer Stuart primary navy
NAVY_DARK = "#0E2241"       # darker navy for accents / footers
GOLD = "#FBCC11"            # Spencer Stuart accent gold
GOLD_SOFT = "#F6E08A"       # softened gold for secondary bars
CREAM = "#F7F4EE"           # light page background, evokes paper
WHITE = "#FFFFFF"
INK = "#1B1B1B"             # body copy
MUTED = "#6B7280"           # secondary text
BORDER = "#E5E1D7"          # hairline borders matching cream

# Status colours used in chart palettes and badges
SUCCESS = "#2E7D5B"
WARNING = "#C98A1A"
DANGER = "#B23A48"

# Sequential palette for categorical bars (current vs previous period)
PALETTE_CURRENT = NAVY
PALETTE_PREVIOUS = GOLD
PALETTE_CATEGORICAL = [NAVY, GOLD, "#3F6491", "#C98A1A", "#7796B5", "#A1885A"]

# Fonts
SERIF_FONT = '"Georgia", "Times New Roman", serif'
SANS_FONT = '"Inter", "Helvetica Neue", "Arial", sans-serif'

# Plotly layout defaults
CHART_MARGIN = dict(l=40, r=20, t=60, b=40)
CHART_HEIGHT = 320

PLOTLY_LAYOUT_DEFAULTS = dict(
    template="plotly_white",
    margin=CHART_MARGIN,
    paper_bgcolor=WHITE,
    plot_bgcolor=WHITE,
    font=dict(family=SANS_FONT, color=INK, size=12),
    title=dict(
        font=dict(family=SERIF_FONT, color=NAVY, size=16),
        x=0.02, xanchor="left", y=0.95,
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=-0.25,
        xanchor="left", x=0,
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=MUTED, size=11),
    ),
    colorway=PALETTE_CATEGORICAL,
)

# Branding assets
LOGO_URL = (
    "https://cdn.cookielaw.org/logos/b51d2c9b-8d53-4695-b601-f32cb832cef7/"
    "56478ccc-982c-427f-bdfe-b87cb415ba0f/d9ced935-47fc-4122-a1c2-a45bf306d6f9/"
    "spencerstuart_blue_trans.png"
)
COMPANY_NAME = "Spencer Stuart"
DASHBOARD_TITLE = "Engagements Performance Report"
DASHBOARD_TAGLINE = "Automated Reporting"

# Timeframe options used in the navbar selector
TIMEFRAME_OPTIONS = [
    {"label": "Month", "value": "month"},
    {"label": "Quarter", "value": "quarter"},
    {"label": "Year", "value": "year"},
]
DEFAULT_TIMEFRAME = "month"

TIMEFRAME_LABELS = {
    "month": ("month", "last month", "previous month"),
    "quarter": ("quarter", "last quarter", "previous quarter"),
    "year": ("year", "last year", "previous year"),
}

USE_REVENUE_WORLD_MAP = True  # flag for the chart with countries

# Country code lookup (data uses ISO-2 codes; Plotly choropleth needs ISO-3)
COUNTRY_ISO3 = {
    "AU": "AUS", "BR": "BRA", "CA": "CAN", "DE": "DEU", "ES": "ESP",
    "FR": "FRA", "JP": "JPN", "NL": "NLD", "SG": "SGP", "UK": "GBR",
    "US": "USA",
}

COUNTRY_NAMES = {
    "AU": "Australia", "BR": "Brazil", "CA": "Canada", "DE": "Germany",
    "ES": "Spain", "FR": "France", "JP": "Japan", "NL": "Netherlands",
    "SG": "Singapore", "UK": "United Kingdom", "US": "United States",
}
