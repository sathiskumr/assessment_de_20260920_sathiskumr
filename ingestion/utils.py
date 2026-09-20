from datetime import date, timedelta
from pathlib import Path

import yaml

# Project root (de-template-repo/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "cities.yml"


def load_cities() -> list[dict]:
    """Load city configuration from config/cities.yml."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config["cities"]


def get_date_range(days: int = 30) -> tuple[str, str]:
    """
    Return start_date and end_date (YYYY-MM-DD) for the last `days` days.
    """
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=days - 1)

    return start_date.isoformat(), end_date.isoformat()