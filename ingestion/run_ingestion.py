from datetime import date, timedelta

from ingestion.client import fetch_weather
from ingestion.loader import create_table, upsert_weather
from ingestion.utils import get_date_range, load_cities


def run_ingestion_for_date(target_date: str) -> int:
    """Load one logical date (YYYY-MM-DD) for every configured city.
    This is what the Airflow task calls, driven by {{ ds }}."""
    cities = load_cities()
    create_table()

    total_rows = 0
    for city in cities:
        rows = fetch_weather(city, target_date, target_date)
        upsert_weather(rows)
        total_rows += len(rows)
        print(f"Loaded {len(rows)} rows for {city['name']} on {target_date}")

    print(f"\nIngestion completed for {target_date}. Total rows: {total_rows}")
    return total_rows


def backfill(days: int = 30) -> int:
    """Local helper: loads the last N days, one logical date at a time."""
    start_date, end_date = get_date_range(days)
    current, end = date.fromisoformat(start_date), date.fromisoformat(end_date)

    total = 0
    while current <= end:
        total += run_ingestion_for_date(current.isoformat())
        current += timedelta(days=1)
    return total


if __name__ == "__main__":
    backfill()