import os
from flask import Flask, request
import psycopg2

app = Flask(__name__)

DB_CFG = dict(
    host=os.environ.get("DB_HOST", "db"),
    dbname=os.environ.get("DB_NAME", "mydb"),
    user=os.environ.get("DB_USER", "myuser"),
    password=os.environ.get("DB_PASSWORD", "ded0972"),
)

def get_conn():
    return psycopg2.connect(**DB_CFG)

@app.route("/health")
def health():
    return "ok\n"

@app.route("/")
def index():
    ip = request.headers.get("X-Real-IP", request.remote_addr) or "unknown"

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS visits (
          id SERIAL PRIMARY KEY,
          visited_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          ip TEXT NOT NULL
        );
    """)

    cur.execute("INSERT INTO visits (ip) VALUES (%s);", (ip,))
    conn.commit()

    cur.close()
    conn.close()

    return "visit saved (docker)\n"

@app.route("/visits")
def visits():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, visited_at, ip FROM visits ORDER BY id DESC LIMIT 10;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return "\n".join([f"{r[0]} | {r[1]} | {r[2]}" for r in rows]) + "\n"
