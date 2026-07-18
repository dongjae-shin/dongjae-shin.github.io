#!/usr/bin/env python3
"""Update _data/visitor_stats.json from Google Analytics Data API."""

from __future__ import annotations

import base64
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "_data" / "visitor_stats.json"


def read_service_account_info() -> dict:
    raw = os.environ.get("GA_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        raise RuntimeError("GA_SERVICE_ACCOUNT_JSON is not set")
    if raw.startswith("{"):
        return json.loads(raw)
    return json.loads(base64.b64decode(raw).decode("utf-8"))


def run_report(client, property_id: str, start_date: str, end_date: str, dimensions: list[str] | None = None):
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

    return client.run_report(
        RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name=name) for name in dimensions or []],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        )
    )


def active_users_total(client, property_id: str, start_date: str, end_date: str) -> int:
    response = run_report(client, property_id, start_date, end_date)
    if not response.rows:
        return 0
    return int(response.rows[0].metric_values[0].value or 0)


def countries(client, property_id: str, start_date: str, end_date: str) -> list[dict]:
    response = run_report(client, property_id, start_date, end_date, ["country", "countryId"])
    rows = []
    for row in response.rows:
        active_users = int(row.metric_values[0].value or 0)
        if active_users == 0:
            continue
        rows.append(
            {
                "country": row.dimension_values[0].value or "Unknown",
                "country_id": row.dimension_values[1].value or "",
                "active_users": active_users,
            }
        )
    return sorted(rows, key=lambda item: item["active_users"], reverse=True)


def main() -> int:
    property_id = os.environ.get("GA_PROPERTY_ID", "").strip()
    if not property_id or not os.environ.get("GA_SERVICE_ACCOUNT_JSON", "").strip():
        print("GA_PROPERTY_ID or GA_SERVICE_ACCOUNT_JSON is not set; leaving visitor stats unchanged.")
        return 0

    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_info(
        read_service_account_info(),
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    client = BetaAnalyticsDataClient(credentials=credentials)

    yesterday = date.today() - timedelta(days=1)
    last_30_start = yesterday - timedelta(days=29)
    all_time_start = os.environ.get("GA_START_DATE", "2020-01-01")
    end_date = yesterday.isoformat()

    data = {
        "configured": True,
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "Google Analytics",
        "date_ranges": {
            "all_time": {
                "label": "All time",
                "start_date": all_time_start,
                "end_date": end_date,
                "active_users": active_users_total(client, property_id, all_time_start, end_date),
            },
            "last_30_days": {
                "label": "Last 30 days",
                "start_date": last_30_start.isoformat(),
                "end_date": end_date,
                "active_users": active_users_total(client, property_id, last_30_start.isoformat(), end_date),
            },
        },
        "countries": countries(client, property_id, all_time_start, end_date),
    }

    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
