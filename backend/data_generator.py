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

DEFAULT_CLIENT_NAME = os.getenv("DEFAULT_CLIENT_NAME", "Cliente Default")
SLEEP_SECONDS = int(os.getenv("DATA_GENERATOR_INTERVAL", "10"))
DEVICE_NAMES = ["Main Meter", "Kitchen", "Living Room", "Bedroom", "Workshop"]


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def ensure_table():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS clients (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS power_consumption (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    device_name TEXT,
                    watts FLOAT,
                    cost_estimated FLOAT,
                    client_id INTEGER
                );
                """
            )
            cur.execute("ALTER TABLE power_consumption ADD COLUMN IF NOT EXISTS client_id INTEGER;")
            conn.commit()


def ensure_clients(conn):
    client_names = [f"Cliente {i}" for i in range(1, 6)]
    with conn.cursor() as cur:
        for name in client_names:
            cur.execute(
                "INSERT INTO clients (name) SELECT %s WHERE NOT EXISTS (SELECT 1 FROM clients WHERE name = %s);",
                (name, name),
            )
        conn.commit()


def get_random_client_id(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM clients WHERE name LIKE 'Cliente %' ORDER BY id LIMIT 5;")
        client_ids = [row[0] for row in cur.fetchall()]
        if not client_ids:
            ensure_clients(conn)
            cur.execute("SELECT id FROM clients WHERE name LIKE 'Cliente %' ORDER BY id LIMIT 5;")
            client_ids = [row[0] for row in cur.fetchall()]
        return random.choice(client_ids)


def get_default_client_id(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM clients WHERE name = %s LIMIT 1;", (DEFAULT_CLIENT_NAME,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO clients (name) VALUES (%s) RETURNING id;", (DEFAULT_CLIENT_NAME,))
        return cur.fetchone()[0]


def insert_random_measurement():
    device_name = random.choice(DEVICE_NAMES)
    watts = round(random.uniform(100.0, 600.0), 2)
    # custo estimado calculado com um preço médio de 0.15 €/kWh e 1 kW = 1000 W
    cost_estimated = round((watts / 1000.0) * 0.15, 4)
    timestamp = datetime.now(timezone.utc)

    with get_db_connection() as conn:
        ensure_clients(conn)
        client_id = get_random_client_id(conn)
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO power_consumption (timestamp, device_name, watts, cost_estimated, client_id) VALUES (%s, %s, %s, %s, %s)",
                (timestamp, device_name, watts, cost_estimated, client_id),
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
