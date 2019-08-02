SELECT
  CORR(cash,
    trip_miles) AS trip_miles_corr,
  CORR(cash,
    standard_pickup_lat) AS pickup_latitude_corr,
  CORR(cash,
    standard_pickup_long) AS pickup_longitude_corr,
  CORR(cash,
    standard_dropoff_lat) AS dropoff_latitude_corr,
  CORR(cash,
    standard_dropoff_long) AS dropoff_longitude_corr,
  CORR(cash,
    start_time) AS dropoff_time_corr,
  CORR(cash,
    year) AS dropoff_year_corr,
  CORR(cash,
    month) AS month_corr,
  CORR(cash,
    day_of_year) AS day_corr,
  CORR(cash,
    day_of_week) AS weekday_corr
FROM
  `ml-sandbox-1-191918.chicagotaxi.chicago_taxi_processed`
