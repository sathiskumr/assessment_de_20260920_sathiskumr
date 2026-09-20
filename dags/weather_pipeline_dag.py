"""
Weather Pipeline DAG

Pipeline:
    Extract & Load -> dbt run -> dbt test

The ingestion task loads weather data for one Airflow logical date (`ds`) into
PostgreSQL. The loader is idempotent, so rerunning the same logical date updates
existing rows instead of creating duplicates.

The DAG supports Airflow catchup/backfill because it always uses the logical
execution date rather than today's date.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]   # /opt/airflow
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from datetime import timedelta

import pendulum
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/dbt"

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "execution_timeout": timedelta(minutes=15),
}


@dag(
    dag_id="weather_pipeline",
    description="Extract Open-Meteo weather data, load to Postgres, transform with dbt.",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 8, 1, tz="Asia/Kolkata"),
    catchup=True,
    max_active_runs=1,
    default_args=default_args,
    tags=["assessment", "weather"],
)
def weather_pipeline():
    @task(task_id="extract_load")
    def extract_load(ds=None):
        """
        Load weather data for a single Airflow logical date.

        The ingestion function reads every configured city from `config/cities.yml`
        and upserts one day's weather into the raw table.
        """
        from ingestion.run_ingestion import run_ingestion_for_date

        rows_loaded = run_ingestion_for_date(ds)
        print(f"Loaded {rows_loaded} rows for logical date {ds}")
        return rows_loaded

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"""
        cd {DBT_DIR} &&
        DBT_PROFILES_DIR={DBT_DIR} dbt run
        """,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"""
        cd {DBT_DIR} &&
        DBT_PROFILES_DIR={DBT_DIR} dbt test
        """,
    )

    extract_load() >> dbt_run >> dbt_test


weather_pipeline()