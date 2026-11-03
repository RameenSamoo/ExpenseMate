from database.database import execute_query
from utils.calculations import (
    calculate_balance,
    calculate_savings,
    calculate_savings_rate,
    calculate_monthly_change
)
from services.budget_service import get_budgets, get_budget_alerts
from services.goal_service import get_goal_alerts, get_goals

def get_dashboard_summary(user_id, month=None, year=None):
    import datetime
    today = datetime.date.today()
    m = int(month) if month else today.month
    y = int(year) if year else today.year

    # Total Income for selected month
    inc_row = execute_query(
        """SELECT COALESCE(SUM(amount), 0.0) as total
           FROM transactions
           WHERE user_id = ? AND transaction_type = 'income'
           AND CAST(strftime('%m', transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?""",
        (user_id, m, y), fetch_one=True
    )
    tot_income = float(inc_row['total']) if inc_row else 0.0

    # Total Expenses for selected month
    exp_row = execute_query(
        """SELECT COALESCE(SUM(amount), 0.0) as total
           FROM transactions
           WHERE user_id = ? AND transaction_type = 'expense'
           AND CAST(strftime('%m', transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?""",
        (user_id, m, y), fetch_one=True
    )
    tot_expense = float(exp_row['total']) if exp_row else 0.0

    # All-time Total Balance
    all_inc_row = execute_query("SELECT COALESCE(SUM(amount), 0.0) as total FROM transactions WHERE user_id = ? AND transaction_type = 'income'", (user_id,), fetch_one=True)
    all_exp_row = execute_query("SELECT COALESCE(SUM(amount), 0.0) as total FROM transactions WHERE user_id = ? AND transaction_type = 'expense'", (user_id,), fetch_one=True)
    tot_balance = calculate_balance(all_inc_row['total'], all_exp_row['total'])

    savings = calculate_savings(tot_income, tot_expense)
    savings_rate = calculate_savings_rate(tot_income, tot_expense)

    # Budget info
    budget_data = get_budgets(user_id, m, y)
    overall_budget = budget_data['overall']['amount']
    budget_remaining = budget_data['overall']['remaining']
    budget_used_pct = budget_data['overall']['percentage']

    # Expense allocation breakdown (donut chart)
    exp_allocation = execute_query(
        """SELECT c.name as category_name, COALESCE(SUM(t.amount), 0.0) as total
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ? AND t.transaction_type = 'expense'
           AND CAST(strftime('%m', t.transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', t.transaction_date) AS INTEGER) = ?
           GROUP BY c.name
           ORDER BY total DESC""",
        (user_id, m, y)
    )

    # Income summary breakdown
    inc_summary = execute_query(
        """SELECT c.name as category_name, COALESCE(SUM(t.amount), 0.0) as total
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ? AND t.transaction_type = 'income'
           AND CAST(strftime('%m', t.transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', t.transaction_date) AS INTEGER) = ?
           GROUP BY c.name
           ORDER BY total DESC""",
        (user_id, m, y)
    )

    # Recent 10 transactions
    recent_txs = execute_query(
        """SELECT t.*, c.name as category_name
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ?
           ORDER BY t.transaction_date DESC, t.id DESC
           LIMIT 10""",
        (user_id,)
    )

    # Combined Alerts
    b_alerts = get_budget_alerts(user_id, m, y)
    g_alerts = get_goal_alerts(user_id)
    combined_alerts = b_alerts + g_alerts

    return {
        'month': m,
        'year': y,
        'metrics': {
            'total_balance': tot_balance,
            'total_income': tot_income,
            'total_expenses': tot_expense,
            'savings': savings,
            'savings_rate': savings_rate,
            'monthly_budget': overall_budget,
            'budget_remaining': budget_remaining,
            'budget_used_percentage': budget_used_pct
        },
        'expense_allocation': exp_allocation,
        'income_summary': inc_summary,
        'budget_categories': budget_data['categories'],
        'recent_transactions': recent_txs,
        'alerts': combined_alerts
    }

def get_income_analytics(user_id, year=None):
    import datetime
    y = int(year) if year else datetime.date.today().year

    # Total income all time & top source
    tot_inc_row = execute_query("SELECT COALESCE(SUM(amount), 0.0) as total FROM transactions WHERE user_id = ? AND transaction_type = 'income'", (user_id,), fetch_one=True)
    tot_income = float(tot_inc_row['total'])

    top_src_row = execute_query(
        """SELECT c.name as source_name, SUM(t.amount) as total
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ? AND t.transaction_type = 'income'
           GROUP BY c.name ORDER BY total DESC LIMIT 1""",
        (user_id,), fetch_one=True
    )
    top_source = top_src_row['source_name'] if top_src_row else 'N/A'

    # Monthly breakdown for chart (Jan-Dec)
    monthly_trend = execute_query(
        """SELECT CAST(strftime('%m', transaction_date) AS INTEGER) as month_num,
                  COALESCE(SUM(amount), 0.0) as total
           FROM transactions
           WHERE user_id = ? AND transaction_type = 'income'
           AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?
           GROUP BY month_num ORDER BY month_num ASC""",
        (user_id, y)
    )

    monthly_dict = {row['month_num']: float(row['total']) for row in monthly_trend}
    chart_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    trend_data = [monthly_dict.get(i, 0.0) for i in range(1, 13)]

    avg_monthly = sum(trend_data) / max(1, len([val for val in trend_data if val > 0])) if any(trend_data) else 0.0

    return {
        'year': y,
        'total_income': tot_income,
        'avg_monthly_income': round(avg_monthly, 2),
        'top_source': top_source,
        'months': chart_months,
        'trend': trend_data
    }

def get_expense_analytics(user_id, year=None):
    import datetime
    y = int(year) if year else datetime.date.today().year

    tot_exp_row = execute_query("SELECT COALESCE(SUM(amount), 0.0) as total FROM transactions WHERE user_id = ? AND transaction_type = 'expense'", (user_id,), fetch_one=True)
    tot_expense = float(tot_exp_row['total'])

    top_cat_row = execute_query(
        """SELECT c.name as category_name, SUM(t.amount) as total
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ? AND t.transaction_type = 'expense'
           GROUP BY c.name ORDER BY total DESC LIMIT 1""",
        (user_id,), fetch_one=True
    )
    top_category = top_cat_row['category_name'] if top_cat_row else 'N/A'

    monthly_trend = execute_query(
        """SELECT CAST(strftime('%m', transaction_date) AS INTEGER) as month_num,
                  COALESCE(SUM(amount), 0.0) as total
           FROM transactions
           WHERE user_id = ? AND transaction_type = 'expense'
           AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?
           GROUP BY month_num ORDER BY month_num ASC""",
        (user_id, y)
    )

    monthly_dict = {row['month_num']: float(row['total']) for row in monthly_trend}
    chart_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    trend_data = [monthly_dict.get(i, 0.0) for i in range(1, 13)]
    daily_avg = sum(trend_data) / 365.0 if y % 4 != 0 else sum(trend_data) / 366.0

    # Category Breakdown
    cat_breakdown = execute_query(
        """SELECT c.name as category_name, COALESCE(SUM(t.amount), 0.0) as total
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ? AND t.transaction_type = 'expense'
           AND CAST(strftime('%Y', t.transaction_date) AS INTEGER) = ?
           GROUP BY c.name ORDER BY total DESC""",
        (user_id, y)
    )

    return {
        'year': y,
        'total_expense': tot_expense,
        'daily_avg': round(daily_avg, 2),
        'top_category': top_category,
        'months': chart_months,
        'trend': trend_data,
        'category_breakdown': cat_breakdown
    }

def get_detailed_analytics(user_id, month=None, year=None):
    import datetime
    today = datetime.date.today()
    m = int(month) if month else today.month
    y = int(year) if year else today.year

    inc_row = execute_query(
        """SELECT COALESCE(SUM(amount), 0.0) as total FROM transactions
           WHERE user_id = ? AND transaction_type = 'income'
           AND CAST(strftime('%m', transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?""",
        (user_id, m, y), fetch_one=True
    )
    tot_inc = float(inc_row['total'])

    exp_row = execute_query(
        """SELECT COALESCE(SUM(amount), 0.0) as total FROM transactions
           WHERE user_id = ? AND transaction_type = 'expense'
           AND CAST(strftime('%m', transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?""",
        (user_id, m, y), fetch_one=True
    )
    tot_exp = float(exp_row['total'])

    sav = calculate_savings(tot_inc, tot_exp)
    sav_rate = calculate_savings_rate(tot_inc, tot_exp)

    # Spending by category
    cats_exp = execute_query(
        """SELECT c.name as category_name, COALESCE(SUM(t.amount), 0.0) as total
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ? AND t.transaction_type = 'expense'
           AND CAST(strftime('%m', t.transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', t.transaction_date) AS INTEGER) = ?
           GROUP BY c.name ORDER BY total DESC""",
        (user_id, m, y)
    )

    highest_cat = cats_exp[0]['category_name'] if cats_exp else 'None'
    lowest_cat = cats_exp[-1]['category_name'] if cats_exp else 'None'

    # Most expensive transaction
    max_tx = execute_query(
        """SELECT t.*, c.name as category_name FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ? AND t.transaction_type = 'expense'
           AND CAST(strftime('%m', t.transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', t.transaction_date) AS INTEGER) = ?
           ORDER BY t.amount DESC LIMIT 1""",
        (user_id, m, y), fetch_one=True
    )

    tx_count_row = execute_query(
        """SELECT COUNT(*) as cnt FROM transactions
           WHERE user_id = ?
           AND CAST(strftime('%m', transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?""",
        (user_id, m, y), fetch_one=True
    )

    # 12 Month cash flow trend
    trend_rows = execute_query(
        """SELECT strftime('%Y-%m', transaction_date) as month_str,
                  transaction_type,
                  COALESCE(SUM(amount), 0.0) as total
           FROM transactions
           WHERE user_id = ?
           GROUP BY month_str, transaction_type
           ORDER BY month_str ASC LIMIT 24""",
        (user_id,)
    )

    return {
        'month': m,
        'year': y,
        'metrics': {
            'total_income': tot_inc,
            'total_expenses': tot_exp,
            'savings': sav,
            'savings_rate': sav_rate,
            'highest_spending_category': highest_cat,
            'lowest_spending_category': lowest_cat,
            'most_expensive_transaction': max_tx,
            'transaction_count': tx_count_row['cnt'] if tx_count_row else 0
        },
        'expense_categories': cats_exp,
        'cash_flow_trend': trend_rows
    }

def get_monthly_comparison(user_id, m1, y1, m2, y2):
    m1_exp = execute_query(
        """SELECT c.name as category_name, COALESCE(SUM(t.amount), 0.0) as total
           FROM categories c
           LEFT JOIN transactions t ON c.id = t.category_id AND t.user_id = ? AND t.transaction_type = 'expense'
           AND CAST(strftime('%m', t.transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', t.transaction_date) AS INTEGER) = ?
           WHERE c.user_id = ? AND c.type = 'expense'
           GROUP BY c.name""",
        (user_id, m1, y1, user_id)
    )
    m1_map = {row['category_name']: float(row['total']) for row in m1_exp}

    m2_exp = execute_query(
        """SELECT c.name as category_name, COALESCE(SUM(t.amount), 0.0) as total
           FROM categories c
           LEFT JOIN transactions t ON c.id = t.category_id AND t.user_id = ? AND t.transaction_type = 'expense'
           AND CAST(strftime('%m', t.transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', t.transaction_date) AS INTEGER) = ?
           WHERE c.user_id = ? AND c.type = 'expense'
           GROUP BY c.name""",
        (user_id, m2, y2, user_id)
    )
    m2_map = {row['category_name']: float(row['total']) for row in m2_exp}

    all_cats = sorted(list(set(m1_map.keys()).union(set(m2_map.keys()))))
    comparison = []

    for cat in all_cats:
        v1 = m1_map.get(cat, 0.0)
        v2 = m2_map.get(cat, 0.0)
        diff = v2 - v1
        pct_change = calculate_monthly_change(v2, v1)
        direction = 'increase' if diff > 0 else ('decrease' if diff < 0 else 'unchanged')

        comparison.append({
            'category_name': cat,
            'month1_amount': v1,
            'month2_amount': v2,
            'difference': diff,
            'percentage_change': pct_change,
            'direction': direction
        })

    return {
        'month1': {'month': m1, 'year': y1},
        'month2': {'month': m2, 'year': y2},
        'categories': comparison
    }
