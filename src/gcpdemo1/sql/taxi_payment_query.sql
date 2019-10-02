SELECT
  IF(payment_type='Cash',1,0) cash,
  EXTRACT(DAYOFWEEK FROM trip_start_timestamp) AS day_of_week,
  (((EXTRACT(HOUR from trip_start_timestamp)*3600)+(EXTRACT(MINUTE from trip_start_timestamp)*60)+(EXTRACT(SECOND from trip_start_timestamp)))/86400) as start_time,
  (((EXTRACT(HOUR from trip_end_timestamp)*3600)+(EXTRACT(MINUTE from trip_end_timestamp)*60)+(EXTRACT(SECOND from trip_end_timestamp)))/86400) as end_time,
  EXTRACT(DAYOFYEAR FROM trip_start_timestamp) as day_of_year,
  EXTRACT(MONTH FROM trip_start_timestamp) as month,
  EXTRACT(YEAR FROM trip_start_timestamp) as year,
  trip_miles,
  pickup_latitude,
  pickup_longitude,
  dropoff_latitude,
  dropoff_longitude
  
FROM
  `bigquery-public-data.chicago_taxi_trips.taxi_trips`
WHERE
  trip_miles > 0
  AND trip_seconds > 0
  AND fare > 0
  AND payment_type in ('Cash', 'Credit Card')
  AND trip_start_timestamp IS NOT NULL
  AND trip_end_timestamp IS NOT NULL
  AND trip_miles IS NOT NULL
  AND pickup_latitude IS NOT NULL
  AND pickup_longitude IS NOT NULL
  AND dropoff_latitude IS NOT NULL
  AND dropoff_longitude IS NOT NULL;
