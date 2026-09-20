with weather as (
    select * from {{ ref('stg_weather_daily') }}
)

select
    city,
    weather_date,
    weather_code,
    temp_max_c,
    temp_min_c,
    temp_mean_c,
    round((temp_max_c - temp_min_c)::numeric, 1)  as temp_range_c,
    precipitation_mm,
    rain_mm,
    precipitation_hours,
    wind_speed_max_kmh,
    wind_gusts_max_kmh,
    round((daylight_seconds / 3600.0)::numeric, 2)  as daylight_hours,
    round((sunshine_seconds / 3600.0)::numeric, 2)  as sunshine_hours,
    precipitation_mm > 0                          as is_rainy_day
from weather