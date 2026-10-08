"""
db.py — PostgreSQL connection and database operations for SecureMed QR.
(Migrated from MySQL for Render's free Postgres tier.)

Tables:
  patients     — encrypted medical records, one row per patient
  access_logs  — every scan attempt (success or failure) for audit trail
"""

import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from flask import g


# ---------------------------------------------------------------------------
# Connection pool — created once when the app starts
# ---------------------------------------------------------------------------

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            dsn=os.environ.get("DATABASE_URL"),
        )
    return _pool


# ---------------------------------------------------------------------------
# Per-request connection (stored on Flask's g object)
# ---------------------------------------------------------------------------

def get_db():
    """Return a Postgres connection for the current request."""
    if "db" not in g:
        g.db = get_pool().getconn()
    return g.db


def close_db(e=None):
    """Release the connection back to the pool at end of request."""
    db = g.pop("db", None)
    if db is not None:
        get_pool().putconn(db)


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

CREATE_PATIENTS = """
CREATE TABLE IF NOT EXISTS patients (
    id            SERIAL PRIMARY KEY,
    qr_id         VARCHAR(64)  NOT NULL UNIQUE,
    encrypted_data BYTEA       NOT NULL,
    iv            BYTEA        NOT NULL,
    gcm_tag       BYTEA        NOT NULL,
    data_hash     CHAR(64)     NOT NULL,
    salt          BYTEA        NOT NULL,
    totp_secret   VARCHAR(64)  NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_ACCESS_LOGS = """
CREATE TABLE IF NOT EXISTS access_logs (
    id             SERIAL PRIMARY KEY,
    patient_qr_id  VARCHAR(64)  NOT NULL,
    responder_ip   VARCHAR(45)  NOT NULL,
    accessed_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    success        BOOLEAN      NOT NULL DEFAULT FALSE,
    failure_reason VARCHAR(128) DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_patient ON access_logs (patient_qr_id);
CREATE INDEX IF NOT EXISTS idx_time    ON access_logs (accessed_at);
"""


def init_db():
    """
    Create both tables if they don't exist.
    Called once from create_app() on startup.
    Render provisions the database itself — we just create tables in it.

    If DATABASE_URL is not set (local dev without PostgreSQL), this is a no-op.
    The landing page and static routes still work — only registration/scan
    endpoints require the database.
    """
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("[db] DATABASE_URL not set — skipping DB init (local dev mode).")
        return
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(CREATE_PATIENTS)
    cursor.execute(CREATE_ACCESS_LOGS)
    cursor.close()
    conn.close()
    print("[db] Tables ready.")


# ---------------------------------------------------------------------------
# Patient helpers
# ---------------------------------------------------------------------------

def insert_patient(qr_id, encrypted_data, iv, gcm_tag,
                   data_hash, salt, totp_secret, password_hash):
    """
    Insert a newly registered patient record.
    Binary values (iv, gcm_tag, salt, encrypted_data) must be bytes —
    psycopg2.Binary() wraps them for BYTEA columns.
    """
    sql = """
        INSERT INTO patients
            (qr_id, encrypted_data, iv, gcm_tag, data_hash, salt, totp_secret, password_hash)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, (
        qr_id,
        psycopg2.Binary(encrypted_data),
        psycopg2.Binary(iv),
        psycopg2.Binary(gcm_tag),
        data_hash,
        psycopg2.Binary(salt),
        totp_secret,
        password_hash,
    ))
    conn.commit()
    cursor.close()


def get_patient(qr_id):
    """
    Fetch a patient row by QR ID.
    Returns a dict or None if not found.
    Note: BYTEA columns come back as memoryview objects — callers that
    need `bytes` (e.g. crypto.decrypt) should wrap with bytes(...),
    which app/routes/responder.py already does.
    """
    sql = """
        SELECT qr_id, encrypted_data, iv, gcm_tag,
               data_hash, salt, totp_secret, password_hash
        FROM patients
        WHERE qr_id = %s
        LIMIT 1
    """
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql, (qr_id,))
    row = cursor.fetchone()
    cursor.close()
    return dict(row) if row else None


def update_patient(qr_id, encrypted_data, iv, gcm_tag, data_hash):
    """Update encrypted record after a patient edits their profile."""
    sql = """
        UPDATE patients
        SET encrypted_data = %s, iv = %s, gcm_tag = %s, data_hash = %s
        WHERE qr_id = %s
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, (
        psycopg2.Binary(encrypted_data),
        psycopg2.Binary(iv),
        psycopg2.Binary(gcm_tag),
        data_hash,
        qr_id,
    ))
    conn.commit()
    cursor.close()


# ---------------------------------------------------------------------------
# Access log helpers
# ---------------------------------------------------------------------------

def log_access(patient_qr_id, responder_ip, success, failure_reason=None):
    """Write one row to access_logs. Call for every scan attempt."""
    sql = """
        INSERT INTO access_logs (patient_qr_id, responder_ip, success, failure_reason)
        VALUES (%s, %s, %s, %s)
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, (patient_qr_id, responder_ip, bool(success), failure_reason))
    conn.commit()
    cursor.close()


def get_access_logs(patient_qr_id, limit=20):
    """Return the most recent access attempts for a patient (for their dashboard)."""
    sql = """
        SELECT responder_ip, accessed_at, success, failure_reason
        FROM access_logs
        WHERE patient_qr_id = %s
        ORDER BY accessed_at DESC
        LIMIT %s
    """
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql, (patient_qr_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    return [dict(r) for r in rows]
