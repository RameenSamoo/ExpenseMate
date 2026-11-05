"""
Migration 001: Add Payment Method & Notes to Transactions, and Rollover Amount to Budgets.
- Schema Migration:
    * transactions.payment_method (TEXT DEFAULT 'Cash')
    * transactions.notes (TEXT DEFAULT '')
    * budgets.rollover_amount (REAL DEFAULT 0.0)
- Data Migration:
    * Backfills existing transactions to 'Cash' and empty string for notes.
    * Backfills existing budgets with rollover_amount = 0.0.
"""

def up(conn):
    """Applies schema changes and migrates existing data."""
    cursor = conn.cursor()

    # 1. Inspect existing columns to guarantee idempotent execution
    cursor.execute("PRAGMA table_info(transactions);")
    tx_columns = [col[1] for col in cursor.fetchall()]

    if 'payment_method' not in tx_columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN payment_method TEXT DEFAULT 'Cash';")
    
    if 'notes' not in tx_columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN notes TEXT DEFAULT '';")

    cursor.execute("PRAGMA table_info(budgets);")
    budget_columns = [col[1] for col in cursor.fetchall()]

    if 'rollover_amount' not in budget_columns:
        cursor.execute("ALTER TABLE budgets ADD COLUMN rollover_amount REAL DEFAULT 0.0;")

    # 2. Data Migration: normalize all legacy existing records
    cursor.execute("""
        UPDATE transactions
        SET payment_method = 'Cash'
        WHERE payment_method IS NULL OR payment_method = '';
    """)

    cursor.execute("""
        UPDATE transactions
        SET notes = ''
        WHERE notes IS NULL;
    """)

    cursor.execute("""
        UPDATE budgets
        SET rollover_amount = 0.0
        WHERE rollover_amount IS NULL;
    """)

def down(conn):
    """Rolls back the migration changes safely."""
    cursor = conn.cursor()

    # SQLite 3.35.0+ supports DROP COLUMN directly
    try:
        cursor.execute("ALTER TABLE transactions DROP COLUMN payment_method;")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE transactions DROP COLUMN notes;")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE budgets DROP COLUMN rollover_amount;")
    except Exception:
        pass
