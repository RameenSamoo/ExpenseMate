from database.database import execute_query
from utils.calculations import (
    calculate_budget_remaining,
    calculate_budget_percentage,
    determine_budget_status
)
from utils.validators import is_non_negative_number

def set_budget(user_id, month, year, amount, category_id=None):
    try:
        month = int(month)
        year = int(year)
    except (ValueError, TypeError):
        return False, "Invalid month or year."

    if month < 1 or month > 12:
        return False, "Month must be between 1 and 12."
    if year < 2000:
        return False, "Year must be 2000 or later."
    if not is_non_negative_number(amount):
        return False, "Budget amount must be zero or positive."

    if category_id:
        category = execute_query(
            "SELECT * FROM categories WHERE id = ? AND user_id = ? AND type = 'expense'",
            (category_id, user_id), fetch_one=True
        )
        if not category:
            return False, "Invalid expense category selected for budget."

        # Check existing category budget
        existing = execute_query(
            "SELECT id FROM budgets WHERE user_id = ? AND category_id = ? AND month = ? AND year = ?",
            (user_id, category_id, month, year), fetch_one=True
        )
        if existing:
            execute_query("UPDATE budgets SET amount = ? WHERE id = ?", (float(amount), existing['id']), commit=True)
            budget_id = existing['id']
        else:
            budget_id = execute_query(
                "INSERT INTO budgets (user_id, category_id, month, year, amount) VALUES (?, ?, ?, ?, ?)",
                (user_id, category_id, month, year, float(amount)), commit=True
            )
    else:
        # Overall monthly budget
        existing = execute_query(
            "SELECT id FROM budgets WHERE user_id = ? AND category_id IS NULL AND month = ? AND year = ?",
            (user_id, month, year), fetch_one=True
        )
        if existing:
            execute_query("UPDATE budgets SET amount = ? WHERE id = ?", (float(amount), existing['id']), commit=True)
            budget_id = existing['id']
        else:
            budget_id = execute_query(
                "INSERT INTO budgets (user_id, category_id, month, year, amount) VALUES (?, NULL, ?, ?, ?)",
                (user_id, month, year, float(amount)), commit=True
            )

    return True, get_budget_by_id(user_id, budget_id)

def get_budget_by_id(user_id, budget_id):
    query = """
        SELECT b.*, c.name as category_name
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.id = ? AND b.user_id = ?
    """
    return execute_query(query, (budget_id, user_id), fetch_one=True)

def delete_budget(user_id, budget_id):
    b = get_budget_by_id(user_id, budget_id)
    if not b:
        return False, "Budget not found or access denied."
    execute_query("DELETE FROM budgets WHERE id = ? AND user_id = ?", (budget_id, user_id), commit=True)
    return True, "Budget deleted successfully."

def get_budgets(user_id, month, year):
    # Overall budget
    overall = execute_query(
        "SELECT * FROM budgets WHERE user_id = ? AND category_id IS NULL AND month = ? AND year = ?",
        (user_id, month, year), fetch_one=True
    )
    overall_amount = float(overall['amount']) if overall else 0.0

    # Total spent in this month
    tot_spent_row = execute_query(
        """SELECT COALESCE(SUM(amount), 0.0) as total
           FROM transactions
           WHERE user_id = ? AND transaction_type = 'expense'
           AND CAST(strftime('%m', transaction_date) AS INTEGER) = ?
           AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?""",
        (user_id, month, year), fetch_one=True
    )
    overall_spent = float(tot_spent_row['total']) if tot_spent_row else 0.0

    # Category budgets & spent
    cat_budgets = execute_query(
        """SELECT b.*, c.name as category_name,
                  (SELECT COALESCE(SUM(t.amount), 0.0)
                   FROM transactions t
                   WHERE t.user_id = b.user_id AND t.category_id = b.category_id AND t.transaction_type = 'expense'
                   AND CAST(strftime('%m', t.transaction_date) AS INTEGER) = b.month
                   AND CAST(strftime('%Y', t.transaction_date) AS INTEGER) = b.year) as spent
           FROM budgets b
           JOIN categories c ON b.category_id = c.id
           WHERE b.user_id = ? AND b.month = ? AND b.year = ?
           ORDER BY c.name ASC""",
        (user_id, month, year)
    )

    processed_categories = []
    for item in cat_budgets:
        b_amt = float(item['amount'])
        s_amt = float(item['spent'])
        pct = calculate_budget_percentage(b_amt, s_amt)
        rem = calculate_budget_remaining(b_amt, s_amt)
        status = determine_budget_status(pct)
        processed_categories.append({
            'id': item['id'],
            'category_id': item['category_id'],
            'category_name': item['category_name'],
            'amount': b_amt,
            'spent': s_amt,
            'remaining': rem,
            'percentage': pct,
            'status': status
        })

    overall_pct = calculate_budget_percentage(overall_amount, overall_spent)
    overall_rem = calculate_budget_remaining(overall_amount, overall_spent)
    overall_status = determine_budget_status(overall_pct)

    return {
        'month': month,
        'year': year,
        'overall': {
            'id': overall['id'] if overall else None,
            'amount': overall_amount,
            'spent': overall_spent,
            'remaining': overall_rem,
            'percentage': overall_pct,
            'status': overall_status
        },
        'categories': processed_categories
    }

def get_budget_alerts(user_id, month, year):
    data = get_budgets(user_id, month, year)
    alerts = []

    # Overall alert
    ov = data['overall']
    if ov['amount'] > 0:
        if ov['status'] == 'Exceeded':
            alerts.append({
                'type': 'danger',
                'title': 'Overall Budget Exceeded',
                'message': f"Your total monthly budget has been exceeded! You spent Rs. {ov['spent']:,.2f} of Rs. {ov['amount']:,.2f}."
            })
        elif ov['status'] == 'Warning':
            alerts.append({
                'type': 'warning',
                'title': 'Overall Budget Warning',
                'message': f"Your total monthly budget is {ov['percentage']}% used. Only Rs. {ov['remaining']:,.2f} remains."
            })

    # Category alerts
    for cat in data['categories']:
        if cat['status'] == 'Exceeded':
            alerts.append({
                'type': 'danger',
                'title': f"{cat['category_name']} Budget Exceeded",
                'message': f"{cat['category_name']} budget has been exceeded ({cat['percentage']}% used). Spent Rs. {cat['spent']:,.2f} of Rs. {cat['amount']:,.2f}."
            })
        elif cat['status'] == 'Warning':
            alerts.append({
                'type': 'warning',
                'title': f"{cat['category_name']} Budget Warning",
                'message': f"{cat['category_name']} budget is {cat['percentage']}% used. Only Rs. {cat['remaining']:,.2f} remains."
            })

    return alerts

def get_yearly_budget_analytics(user_id, year):
    try:
        year = int(year)
    except (ValueError, TypeError):
        import datetime
        year = datetime.date.today().year

    # 1. Total annual overall budget set across all months
    overall_budgets = execute_query(
        "SELECT month, amount FROM budgets WHERE user_id = ? AND category_id IS NULL AND year = ?",
        (user_id, year)
    )
    month_overall_map = {row['month']: float(row['amount']) for row in overall_budgets}
    annual_overall_budget = sum(month_overall_map.values())

    # 2. Total spent per month in this year
    monthly_expenses = execute_query(
        """SELECT CAST(strftime('%m', transaction_date) AS INTEGER) as month_num,
                  COALESCE(SUM(amount), 0.0) as total
           FROM transactions
           WHERE user_id = ? AND transaction_type = 'expense'
           AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?
           GROUP BY month_num""",
        (user_id, year)
    )
    month_spent_map = {row['month_num']: float(row['total']) for row in monthly_expenses}
    annual_total_spent = sum(month_spent_map.values())

    # 3. Monthly Breakdown (Jan-Dec) for chart
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_breakdown = []
    budget_trend = []
    spent_trend = []

    for m in range(1, 13):
        b_amt = month_overall_map.get(m, 0.0)
        s_amt = month_spent_map.get(m, 0.0)
        pct = calculate_budget_percentage(b_amt, s_amt)
        monthly_breakdown.append({
            'month': m,
            'month_name': month_names[m-1],
            'budget': b_amt,
            'spent': s_amt,
            'percentage': pct,
            'remaining': calculate_budget_remaining(b_amt, s_amt)
        })
        budget_trend.append(b_amt)
        spent_trend.append(s_amt)

    # 4. Category-level annual budgets & spent
    cat_budgets = execute_query(
        """SELECT c.id as category_id, c.name as category_name,
                  COALESCE(SUM(b.amount), 0.0) as annual_budget,
                  (SELECT COALESCE(SUM(t.amount), 0.0)
                   FROM transactions t
                   WHERE t.user_id = c.user_id AND t.category_id = c.id AND t.transaction_type = 'expense'
                   AND CAST(strftime('%Y', t.transaction_date) AS INTEGER) = ?) as annual_spent
           FROM categories c
           LEFT JOIN budgets b ON c.id = b.category_id AND b.year = ?
           WHERE c.user_id = ? AND c.type = 'expense'
           GROUP BY c.id, c.name
           HAVING annual_budget > 0 OR annual_spent > 0
           ORDER BY c.name ASC""",
        (year, year, user_id)
    )

    processed_categories = []
    for item in cat_budgets:
        b_amt = float(item['annual_budget'])
        s_amt = float(item['annual_spent'])
        pct = calculate_budget_percentage(b_amt, s_amt)
        rem = calculate_budget_remaining(b_amt, s_amt)
        status = determine_budget_status(pct)
        processed_categories.append({
            'category_id': item['category_id'],
            'category_name': item['category_name'],
            'annual_budget': b_amt,
            'annual_spent': s_amt,
            'remaining': rem,
            'percentage': pct,
            'status': status
        })

    annual_pct = calculate_budget_percentage(annual_overall_budget, annual_total_spent)
    annual_rem = calculate_budget_remaining(annual_overall_budget, annual_total_spent)
    annual_status = determine_budget_status(annual_pct)

    return {
        'year': year,
        'overall': {
            'annual_budget': annual_overall_budget,
            'annual_spent': annual_total_spent,
            'annual_remaining': annual_rem,
            'percentage': annual_pct,
            'status': annual_status
        },
        'months': month_names,
        'budget_trend': budget_trend,
        'spent_trend': spent_trend,
        'monthly_breakdown': monthly_breakdown,
        'categories': processed_categories
    }

