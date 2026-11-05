# Part A — Migration Report: Database Schema & Data Evolution

| Item | Details |
| :--- | :--- |
| **System** | ExpenseMate — Personal Expense Manager |
| **Target** | Database Schema & Data Migration (Transactions & Budgets) |
| **Migration Version** | `001_add_payment_method_and_notes` |
| **Technology** | SQLite 3, Python Migration Framework |

---

## 1. Background & Current (Before) State
In Assignment 01, ExpenseMate tracked financial transactions with a minimal relational schema:
- `transactions`: Only supported `user_id`, `category_id`, `transaction_type`, `amount`, `description`, and `transaction_date`.
- `budgets`: Stored monthly budget limits per user and optional category.

### Limitations of Before State:
1. **Lack of Payment Channel Identification**: Users could not distinguish whether an expense was paid via Cash, Credit Card, Debit Card, Bank Transfer, or Mobile Wallet.
2. **Missing Transaction Notes**: Users could not record supplementary memo details or contextual notes separate from short descriptions.
3. **No Rollover Budgeting**: Budgets had no concept of carrying forward unspent funds (`rollover_amount`).
4. **No Versioned Migration Capability**: Schema changes required either dropping tables or manual destructive SQL scripts, risking data loss in production.

---

## 2. Target State & Architectural Solution
The target state introduces a repeatable, version-controlled database migration framework and evolves both the database schema and existing data:
1. **Versioned Migration Runner (`migrations/migrator.py` & `manage_migrations.py`)**:
   - Maintains an immutable `schema_migrations` table.
   - Detects pending migrations, executes them sequentially in atomic transactions, and records completion.
   - Supports safe bidirectional migration (`up` and `down`/rollback).
2. **Schema & Data Migration (`migrations/001_add_payment_method_and_notes.py`)**:
   - `transactions.payment_method`: `TEXT DEFAULT 'Cash'` (enforcing default values).
   - `transactions.notes`: `TEXT DEFAULT ''` (contextual metadata).
   - `budgets.rollover_amount`: `REAL DEFAULT 0.0`.
   - **Data Normalization**: Automatically scans all pre-existing rows and updates `NULL` or empty records with `'Cash'` and `'0.0'`, ensuring zero orphaned data.

---

## 3. Step-by-Step Procedure Performed

```mermaid
sequenceDiagram
    autonumber
    participant App as Application / CLI
    participant Migrator as Migration Runner
    participant DB as SQLite Database
    participant Table as schema_migrations

    App->>Migrator: run_migrations(conn)
    Migrator->>Table: Query applied versions
    Table-->>Migrator: [versions applied]
    Migrator->>DB: Check table columns (PRAGMA table_info)
    Migrator->>DB: ALTER TABLE transactions ADD COLUMN payment_method
    Migrator->>DB: ALTER TABLE transactions ADD COLUMN notes
    Migrator->>DB: ALTER TABLE budgets ADD COLUMN rollover_amount
    Migrator->>DB: Backfill legacy data (SET payment_method='Cash', rollover_amount=0.0)
    Migrator->>Table: INSERT INTO schema_migrations (version '001')
    Migrator->>DB: COMMIT TRANSACTION
    Migrator-->>App: Successfully applied [001]
```

1. **Safety Analysis & Scripting**: Authored `migrations/001_add_payment_method_and_notes.py` using non-destructive DDL and idempotent checks.
2. **Backfill Query Execution**: Executed `UPDATE` queries ensuring historical transactions retain full validity.
3. **Application Layer Integration**: Updated `database/database.py` to auto-trigger `run_migrations()` during startup, and provided `manage_migrations.py` for command-line control.
4. **Backward Compatibility**: Updated `add_transaction()` and `update_transaction()` with default arguments so legacy callers continue operating without modification.

---

## 4. Risks, Compatibility & Mitigations

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Data Loss on Alteration** | Accidental loss of legacy Assignment 01 transaction history | SQLite column additions are executed with `ALTER TABLE ADD COLUMN`, which does not modify or re-encode existing row storage. |
| **Incomplete Legacy Rows** | `NULL` values breaking queries expecting strings | Data migration step immediately runs an explicit backfill setting legacy rows to `'Cash'` and empty notes. |
| **Failed Migration State** | Database left in half-applied state | All migration actions are wrapped in SQLite connection transactions; failures trigger immediate `ROLLBACK`. |
| **API Consumer Breakage** | Existing frontend forms missing payment method payload | Controllers and services provide fallback default values (`payment_method='Cash'`) if omitted from incoming requests. |

---

## 5. Verification Evidence
A dedicated migration test suite (`tests/test_migration.py`) was executed with the following test cases:
1. `test_migration_up_and_data_preservation`: Verifies pre-migration schema, runs migration, asserts schema changes, and proves 100% preservation of pre-existing records with backfilled defaults.
2. `test_migration_idempotency`: Verifies running migrations repeatedly does not duplicate actions or raise errors.
3. `test_migration_rollback`: Verifies clean down-migration and removal from `schema_migrations`.

### Test Execution Result:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\.gemini\antigravity\scratch\expensemate
collected 3 items

tests\test_migration.py ...                                              [100%]

============================== 3 passed in 0.57s ==============================
```

All 13 project tests (10 regression tests + 3 migration tests) passed with 0 failures, proving that the migration successfully evolves the system without regression.
