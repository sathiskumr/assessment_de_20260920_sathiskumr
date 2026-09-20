select
    city,
    weather_date,
    count(*) as n_rows
from {{ ref('fct_city_daily') }}
group by city, weather_date
having count(*) > 1