import os
import sys

# Ensure parent directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
from database.database import init_db, get_db

DEFAULT_EXPENSE_CATEGORIES = [
    'Food', 'Transport', 'Shopping', 'Bills', 'Education',
    'Entertainment', 'Healthcare', 'Rent', 'Utilities', 'Other'
]

DEFAULT_INCOME_CATEGORIES = [
    'Salary', 'Freelancing', 'Business', 'Allowance', 'Investment', 'Gift', 'Other'
]

def seed_default_categories(conn, user_id):
    """Populates standard expense and income categories for a given user."""
    for cat in DEFAULT_EXPENSE_CATEGORIES:
        conn.execute(
            "INSERT OR IGNORE INTO categories (user_id, name, type) VALUES (?, ?, 'expense')",
            (user_id, cat)
        )
    for cat in DEFAULT_INCOME_CATEGORIES:
        conn.execute(
            "INSERT OR IGNORE INTO categories (user_id, name, type) VALUES (?, ?, 'income')",
            (user_id, cat)
        )

def seed_database():
    """Initializes schema and seeds demo account data."""
    init_db()

    with get_db() as conn:
        # Check if demo user exists
        demo_email = 'demo@expensemate.com'
        cursor = conn.execute("SELECT id FROM users WHERE email = ?", (demo_email,))
        user_row = cursor.fetchone()

        if user_row:
            user_id = user_row['id']
        else:
            pwd_hash = generate_password_hash('Demo123!')
            cursor = conn.execute(
                "INSERT INTO users (full_name, email, password_hash, currency) VALUES (?, ?, ?, ?)",
                ('Demo User', demo_email, pwd_hash, 'PKR')
            )
            user_id = cursor.lastrowid

        seed_default_categories(conn, user_id)

        # Get category IDs mapping
        cursor = conn.execute("SELECT id, name, type FROM categories WHERE user_id = ?", (user_id,))
        cat_map = {(row['name'], row['type']): row['id'] for row in cursor.fetchall()}

        # Seed sample income transactions if empty
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM transactions WHERE user_id = ?", (user_id,))
        if cursor.fetchone()['cnt'] == 0:
            # 2026-09 transactions
            incomes = [
                (cat_map.get(('Salary', 'income')), 100000, 'Monthly Salary - September', '2026-09-01'),
                (cat_map.get(('Freelancing', 'income')), 10000, 'Web Design Project', '2026-09-05'),
                (cat_map.get(('Other', 'income')), 5000, 'Dividend Payout', '2026-09-10'),
                (cat_map.get(('Salary', 'income')), 100000, 'Monthly Salary - August', '2026-08-01'),
                (cat_map.get(('Freelancing', 'income')), 15000, 'Consulting Client', '2026-08-12')
            ]
            for cat_id, amt, desc, dt in incomes:
                if cat_id:
                    conn.execute(
                        "INSERT INTO transactions (user_id, category_id, transaction_type, amount, description, transaction_date) VALUES (?, ?, 'income', ?, ?, ?)",
                        (user_id, cat_id, amt, desc, dt)
                    )

            # Sample expenses
            expenses = [
                (cat_map.get(('Food', 'expense')), 16000, 'Monthly Groceries & Supermarket', '2026-09-02'),
                (cat_map.get(('Transport', 'expense')), 4500, 'Fuel & Vehicle Maintenance', '2026-09-03'),
                (cat_map.get(('Shopping', 'expense')), 9000, 'Clothing & Electronics', '2026-09-04'),
                (cat_map.get(('Bills', 'expense')), 7500, 'Electricity & Broadband Bill', '2026-09-06'),
                (cat_map.get(('Food', 'expense')), 18000, 'August Groceries', '2026-08-05'),
                (cat_map.get(('Transport', 'expense')), 9000, 'August Fuel', '2026-08-10'),
                (cat_map.get(('Shopping', 'expense')), 5000, 'August Shopping', '2026-08-15')
            ]
            for cat_id, amt, desc, dt in expenses:
                if cat_id:
                    conn.execute(
                        "INSERT INTO transactions (user_id, category_id, transaction_type, amount, description, transaction_date) VALUES (?, ?, 'expense', ?, ?, ?)",
                        (user_id, cat_id, amt, desc, dt)
                    )

        # Seed sample budgets if empty
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM budgets WHERE user_id = ?", (user_id,))
        if cursor.fetchone()['cnt'] == 0:
            # Overall monthly budget
            conn.execute(
                "INSERT INTO budgets (user_id, category_id, month, year, amount) VALUES (?, NULL, 9, 2026, 70000)",
                (user_id,)
            )
            # Category budgets
            cat_budgets = [
                (cat_map.get(('Food', 'expense')), 9, 2026, 20000),
                (cat_map.get(('Transport', 'expense')), 9, 2026, 10000),
                (cat_map.get(('Shopping', 'expense')), 9, 2026, 15000),
                (cat_map.get(('Bills', 'expense')), 9, 2026, 15000)
            ]
            for cat_id, m, y, amt in cat_budgets:
                if cat_id:
                    conn.execute(
                        "INSERT INTO budgets (user_id, category_id, month, year, amount) VALUES (?, ?, ?, ?, ?)",
                        (user_id, cat_id, m, y, amt)
                    )

        # Seed sample goals if empty
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM goals WHERE user_id = ?", (user_id,))
        if cursor.fetchone()['cnt'] == 0:
            goals = [
                ('Emergency Fund', '2026-01-01', '2027-09-01', 300000, 50000, 150000, 12500, 'High', 'On Track', 'Safety net for 6 months'),
                ('New Laptop', '2026-06-01', '2026-12-31', 150000, 30000, 60000, 10000, 'Medium', 'Behind Schedule', 'Workstation upgrade'),
                ('Vacation Trip', '2026-03-01', '2027-06-01', 125000, 10000, 40000, 3500, 'Low', 'On Track', 'Summer getaway')
            ]
            for name, s_dt, t_dt, t_amt, st_amt, c_amt, m_tgt, prio, st, nts in goals:
                cursor = conn.execute(
                    """INSERT INTO goals (user_id, goal_name, start_date, target_date, target_amount,
                       starting_amount, current_amount, monthly_target, priority, status, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, name, s_dt, t_dt, t_amt, st_amt, c_amt, m_tgt, prio, st, nts)
                )
                goal_id = cursor.lastrowid
                # Seed contribution history for each goal
                conn.execute(
                    "INSERT INTO goal_contributions (goal_id, amount, contribution_date, description) VALUES (?, ?, ?, ?)",
                    (goal_id, (c_amt - st_amt) / 2, '2026-07-01', 'Initial deposit')
                )
                conn.execute(
                    "INSERT INTO goal_contributions (goal_id, amount, contribution_date, description) VALUES (?, ?, ?, ?)",
                    (goal_id, (c_amt - st_amt) / 2, '2026-08-15', 'Monthly savings allocation')
                )

        # Seed sample recurring expenses
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM recurring_expenses WHERE user_id = ?", (user_id,))
        if cursor.fetchone()['cnt'] == 0:
            recurs = [
                ('Internet Bill', cat_map.get(('Bills', 'expense')), 3000, 'monthly', '2026-01-01', None),
                ('Netflix Subscription', cat_map.get(('Entertainment', 'expense')), 1500, 'monthly', '2026-01-01', None)
            ]
            for name, cat_id, amt, freq, s_dt, e_dt in recurs:
                if cat_id:
                    conn.execute(
                        "INSERT INTO recurring_expenses (user_id, name, category_id, amount, frequency, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (user_id, name, cat_id, amt, freq, s_dt, e_dt)
                    )

    print("Database successfully initialized and seeded with demo data!")

if __name__ == '__main__':
    seed_database()
