select *
from {{ ref('fct_city_daily') }}
where temp_max_c < temp_min_c
   or temp_max_c > 60
   or temp_min_c < -50
   or precipitation_mm < 0