CREATE TABLE "andrewdoss/air_quality"."pm_measurements" (
    "datetime" timestamp with time zone DEFAULT NOW(),
    "location" text,
    "sensor_id" integer,
    "pm_2_5" real,
    "pm_10" real
)