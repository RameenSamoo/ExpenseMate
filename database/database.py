import sqlite3
import os
from contextlib import contextmanager

def get_db_path():
    """Gets the database path from Flask app context if available, else from Config."""
    try:
        from flask import current_app
        return current_app.config['DATABASE_PATH']
    except RuntimeError:
        # Outside Flask app context (e.g., standalone seed script)
        from config import Config
        return Config.DATABASE_PATH

@contextmanager
def get_db():
    """Context manager for SQLite database connections."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Reads schema.sql and initializes the SQLite database tables."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    with get_db() as conn:
        conn.executescript(schema_sql)

def execute_query(query, params=(), fetch_all=None, fetch_one=False, commit=False):
    """Utility helper for executing parameterized SQL queries safely."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            return cursor.lastrowid
        if fetch_one:
            row = cursor.fetchone()
            return dict(row) if row else None
        if fetch_all or fetch_all is None:
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        return None
