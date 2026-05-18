import os
import random
import time
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import execute_values

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "opspulse"),
}

SLEEP_SECONDS = int(os.getenv("DATA_GENERATOR_INTERVAL", "10"))
DEVICE_NAMES = ["Main Meter", "Kitchen", "Living Room", "Bedroom", "Workshop"]


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def ensure_table():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS power_consumption (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    device_name TEXT,
                    watts FLOAT,
                    cost_estimated FLOAT
                );
                """
            )
            conn.commit()


def insert_random_measurement():
    device_name = random.choice(DEVICE_NAMES)
    watts = round(random.uniform(100.0, 600.0), 2)
    # custo estimado calculado com um preço médio de 0.15 €/kWh e 1 kW = 1000 W
    cost_estimated = round((watts / 1000.0) * 0.15, 4)
    timestamp = datetime.now(timezone.utc)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO power_consumption (timestamp, device_name, watts, cost_estimated) VALUES (%s, %s, %s, %s)",
                (timestamp, device_name, watts, cost_estimated),
            )
            conn.commit()

    print(f"[DATA_GENERATOR] {timestamp.isoformat()} | {device_name} | {watts}W | €{cost_estimated}")


if __name__ == "__main__":
    print("Starting data generator...")
    while True:
        try:
            ensure_table()
            insert_random_measurement()
        except Exception as exc:
            print(f"[DATA_GENERATOR] Error: {exc}")
        time.sleep(SLEEP_SECONDS)
