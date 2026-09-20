with source as (

    select * from {{ source('raw', 'raw_weather_daily') }}

),

renamed as (

    select
        city,
        date                 as weather_date,
        weather_code,
        temperature_2m_max   as temp_max_c,
        temperature_2m_min   as temp_min_c,
        temperature_2m_mean  as temp_mean_c,
        precipitation_sum    as precipitation_mm,
        rain_sum             as rain_mm,
        precipitation_hours,
        wind_speed_10m_max   as wind_speed_max_kmh,
        wind_gusts_10m_max   as wind_gusts_max_kmh,
        daylight_duration    as daylight_seconds,
        sunshine_duration    as sunshine_seconds,
        ingested_at

    from source

)

select * from renamed