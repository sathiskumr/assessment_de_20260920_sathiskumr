import os

import psycopg2
from psycopg2.extras import execute_values

def get_connection():
    """Create a PostgreSQL connection using environment variables."""

    return psycopg2.connect(
        host        =os.getenv("WAREHOUSE_HOST", "localhost"),
        port        =os.getenv("WAREHOUSE_PORT", "5432"),
        dbname      =os.getenv("WAREHOUSE_DB", "warehouse"),
        user        =os.getenv("WAREHOUSE_USER", "de"),
        password    =os.getenv("WAREHOUSE_PASSWORD", "de"),
    )


def create_table():
    """Create the raw weather table if it does not already exist."""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS raw_weather_daily (
        city                TEXT NOT NULL,
        date                DATE NOT NULL,
        weather_code        INTEGER,
        temperature_2m_max  DOUBLE PRECISION,
        temperature_2m_min  DOUBLE PRECISION,
        temperature_2m_mean DOUBLE PRECISION,
        precipitation_sum   DOUBLE PRECISION,
        rain_sum            DOUBLE PRECISION,
        precipitation_hours DOUBLE PRECISION,
        wind_speed_10m_max  DOUBLE PRECISION,
        wind_gusts_10m_max  DOUBLE PRECISION,
        daylight_duration   DOUBLE PRECISION,
        sunshine_duration   DOUBLE PRECISION,
        ingested_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

        PRIMARY KEY (city, date)
    );
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
        conn.commit()


def upsert_weather(rows: list[dict]) -> int:
    """Insert or update weather rows into the raw table."""

    insert_sql = """
    INSERT INTO raw_weather_daily (
        city,
        date,
        weather_code,
        temperature_2m_max,
        temperature_2m_min,
        temperature_2m_mean,
        precipitation_sum,
        rain_sum,
        precipitation_hours,
        wind_speed_10m_max,
        wind_gusts_10m_max,
        daylight_duration,
        sunshine_duration
    )
    VALUES %s
    ON CONFLICT (city, date)
    DO UPDATE SET
        weather_code            = EXCLUDED.weather_code,
        temperature_2m_max      = EXCLUDED.temperature_2m_max,
        temperature_2m_min      = EXCLUDED.temperature_2m_min,
        temperature_2m_mean     = EXCLUDED.temperature_2m_mean,
        precipitation_sum       = EXCLUDED.precipitation_sum,
        rain_sum                = EXCLUDED.rain_sum,
        precipitation_hours     = EXCLUDED.precipitation_hours,
        wind_speed_10m_max      = EXCLUDED.wind_speed_10m_max,
        wind_gusts_10m_max      = EXCLUDED.wind_gusts_10m_max,
        daylight_duration       = EXCLUDED.daylight_duration,
        sunshine_duration       = EXCLUDED.sunshine_duration,
        ingested_at             = CURRENT_TIMESTAMP;
    """

    values = [
        (
            row["city"],
            row["date"],
            row["weather_code"],
            row["temperature_2m_max"],
            row["temperature_2m_min"],
            row["temperature_2m_mean"],
            row["precipitation_sum"],
            row["rain_sum"],
            row["precipitation_hours"],
            row["wind_speed_10m_max"],
            row["wind_gusts_10m_max"],
            row["daylight_duration"],
            row["sunshine_duration"],
        )
        for row in rows
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, values)
        conn.commit()

    return len(values)