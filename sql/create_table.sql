CREATE TABLE IF NOT EXISTS green_trips (
    id SERIAL PRIMARY KEY,
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    trip_distance NUMERIC,
    fare_amount NUMERIC,
    pickup_location_id INTEGER,
    dropoff_location_id INTEGER,
    vendor_id INTEGER,
    duracion_minutos NUMERIC,
    velocidad_mph NUMERIC
);
