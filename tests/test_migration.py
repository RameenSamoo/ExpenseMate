"""
Test Suite for Database Schema & Data Migration (Part A - Migration).
Demonstrates:
1. Baseline database initialization without new columns.
2. Legacy record population.
3. Safe execution of migration script 001.
4. Data integrity verification (all legacy data preserved with defaults applied).
5. New column feature verification (inserting custom payment methods and notes).
6. Safe migration rollback verification.
"""
import sqlite3
import pytest
import os
import tempfile
from migrations.migrator import (
    run_migrations,
    rollback_migration,
    get_applied_migrations,
    ensure_migration_table
)

BASELINE_SCHEMA_V1 = """
PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    currency TEXT DEFAULT 'PKR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, name, type)
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    transaction_type TEXT CHECK(transaction_type IN ('income', 'expense')) NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    description TEXT,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER,
    month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
    year INTEGER NOT NULL CHECK(year >= 2000),
    amount REAL NOT NULL CHECK(amount >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);
"""

@pytest.fixture
def legacy_db():
    """Sets up an in-memory or temp SQLite database with Assignment 01 baseline schema and test data."""
    fd, path = tempfile.mkstemp(suffix='.db')
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(BASELINE_SCHEMA_V1)

    # Seed baseline user, category, and transactions
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (full_name, email, password_hash) VALUES ('Baseline User', 'base@test.com', 'hash123');")
    user_id = cursor.lastrowid

    cursor.execute("INSERT INTO categories (user_id, name, type) VALUES (?, 'Food', 'expense');", (user_id,))
    cat_food_id = cursor.lastrowid

    cursor.execute("INSERT INTO categories (user_id, name, type) VALUES (?, 'Salary', 'income');", (user_id,))
    cat_salary_id = cursor.lastrowid

    # Insert legacy transactions WITHOUT payment_method or notes
    cursor.execute("""
        INSERT INTO transactions (user_id, category_id, transaction_type, amount, description, transaction_date)
        VALUES (?, ?, 'expense', 450.50, 'Groceries pre-migration', '2026-09-01')
    """, (user_id, cat_food_id))

    cursor.execute("""
        INSERT INTO transactions (user_id, category_id, transaction_type, amount, description, transaction_date)
        VALUES (?, ?, 'income', 75000.00, 'Monthly Paycheck pre-migration', '2026-09-01')
    """, (user_id, cat_salary_id))

    # Insert legacy budget WITHOUT rollover_amount
    cursor.execute("""
        INSERT INTO budgets (user_id, category_id, month, year, amount)
        VALUES (?, ?, 9, 2026, 20000.0)
    """, (user_id, cat_food_id))

    conn.commit()

    yield conn, user_id, cat_food_id

    conn.close()
    os.close(fd)
    if os.path.exists(path):
        try:
            os.unlink(path)
        except OSError:
            pass

def test_migration_up_and_data_preservation(legacy_db):
    conn, user_id, cat_food_id = legacy_db
    cursor = conn.cursor()

    # Step 1: Confirm pre-migration state (columns do not exist)
    cursor.execute("PRAGMA table_info(transactions);")
    columns_before = [col[1] for col in cursor.fetchall()]
    assert 'payment_method' not in columns_before
    assert 'notes' not in columns_before

    cursor.execute("PRAGMA table_info(budgets);")
    budget_cols_before = [col[1] for col in cursor.fetchall()]
    assert 'rollover_amount' not in budget_cols_before

    # Step 2: Execute Migration
    applied = run_migrations(conn)
    assert '001' in applied

    # Step 3: Verify schema reflects target state
    cursor.execute("PRAGMA table_info(transactions);")
    columns_after = [col[1] for col in cursor.fetchall()]
    assert 'payment_method' in columns_after
    assert 'notes' in columns_after

    cursor.execute("PRAGMA table_info(budgets);")
    budget_cols_after = [col[1] for col in cursor.fetchall()]
    assert 'rollover_amount' in budget_cols_after

    # Step 4: Verify legacy data is preserved with defaults backfilled
    cursor.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY id ASC;", (user_id,))
    tx_rows = cursor.fetchall()
    assert len(tx_rows) == 2

    # Check grocery transaction
    assert tx_rows[0]['description'] == 'Groceries pre-migration'
    assert tx_rows[0]['amount'] == 450.50
    assert tx_rows[0]['payment_method'] == 'Cash'
    assert tx_rows[0]['notes'] == ''

    # Check salary transaction
    assert tx_rows[1]['description'] == 'Monthly Paycheck pre-migration'
    assert tx_rows[1]['amount'] == 75000.00
    assert tx_rows[1]['payment_method'] == 'Cash'

    # Check budget legacy row
    cursor.execute("SELECT * FROM budgets WHERE user_id = ?;", (user_id,))
    b_rows = cursor.fetchall()
    assert len(b_rows) == 1
    assert b_rows[0]['amount'] == 20000.0
    assert b_rows[0]['rollover_amount'] == 0.0

    # Step 5: Test new capability — insert with custom payment method and notes
    cursor.execute("""
        INSERT INTO transactions (user_id, category_id, transaction_type, amount, description, transaction_date, payment_method, notes)
        VALUES (?, ?, 'expense', 1200.00, 'Dinner with team', '2026-09-02', 'Credit Card', 'Office celebration')
    """, (user_id, cat_food_id))
    conn.commit()

    cursor.execute("SELECT * FROM transactions WHERE description = 'Dinner with team';")
    new_row = cursor.fetchone()
    assert new_row['payment_method'] == 'Credit Card'
    assert new_row['notes'] == 'Office celebration'

def test_migration_idempotency(legacy_db):
    """Running migrations repeatedly must not fail or corrupt data."""
    conn, _, _ = legacy_db
    applied1 = run_migrations(conn)
    assert '001' in applied1

    # Second run should detect all migrations already applied
    applied2 = run_migrations(conn)
    assert applied2 == []

def test_migration_rollback(legacy_db):
    """Rollback must safely remove target version and update tracking."""
    conn, _, _ = legacy_db
    run_migrations(conn)
    assert '001' in get_applied_migrations(conn)

    # Roll back
    rolled_back = rollback_migration(conn)
    assert '001' in rolled_back
    assert '001' not in get_applied_migrations(conn)
