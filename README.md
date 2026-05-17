# Spencer Stuart - Engagements Performance Dashboard

An automated Dash report for the Spencer Stuart leadership advisory practice.

## Project layout

```
SpencerStuart_dashboard/
  app.py                 Dash entry point (run "python app.py")
  requirements.txt
  data/
    engagements.csv
    milestones.csv
  assets/
    styles.css           Custom Spencer Stuart theme (auto-loaded by Dash)
  src/
    config.py            Brand palette, paths, layout defaults
    data_processing.py   CSV loading, type casting, data-quality flags
    metrics.py           KPI computations (revenue, counts, rates, ...)
    charts.py            Plotly figure factories (six charts)
    layout.py            Dash layout components (navbar, filters, cards, ...)
    pdf_report.py        Branded ReportLab PDF (server-side download)
```

## Running locally

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:8050>
