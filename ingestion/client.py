from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

DAILY_FIELDS = [
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "rain_sum",
    "precipitation_hours",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "daylight_duration",
    "sunshine_duration",
]


def _create_session() -> Session:
    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )

    session = Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_weather(city, start_date, end_date):
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(DAILY_FIELDS),
        "timezone": "auto",
    }

    response = _create_session().get(BASE_URL, params=params, timeout=30,)
    response.raise_for_status()

    daily = response.json()["daily"]

    rows = []

    for i, weather_date in enumerate(daily["time"]):
        row = {
            "city": city["name"],
            "date": weather_date,
        }

        for field in DAILY_FIELDS:
            row[field] = daily[field][i]

        rows.append(row)

    return rows