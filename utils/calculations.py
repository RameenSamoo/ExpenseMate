from datetime import datetime, date
import math

def calculate_balance(total_income, total_expenses):
    """Returns Net Balance = Total Income - Total Expenses."""
    return round(float(total_income or 0.0) - float(total_expenses or 0.0), 2)

def calculate_savings(total_income, total_expenses):
    """Returns Savings = Total Income - Total Expenses."""
    return round(float(total_income or 0.0) - float(total_expenses or 0.0), 2)

def calculate_savings_rate(total_income, total_expenses):
    """Returns Savings Rate percentage = (Savings / Income) * 100."""
    inc = float(total_income or 0.0)
    exp = float(total_expenses or 0.0)
    if inc <= 0:
        return 0.0
    sav = inc - exp
    return round((sav / inc) * 100.0, 1)

def calculate_budget_remaining(budget_amount, spent_amount):
    """Returns Remaining Budget = Budget Amount - Spent Amount."""
    return round(float(budget_amount or 0.0) - float(spent_amount or 0.0), 2)

def calculate_budget_percentage(budget_amount, spent_amount):
    """Returns Budget used percentage = (Spent / Budget) * 100."""
    b_amt = float(budget_amount or 0.0)
    s_amt = float(spent_amount or 0.0)
    if b_amt <= 0:
        return 0.0
    return round((s_amt / b_amt) * 100.0, 1)

def determine_budget_status(percentage):
    """
    Returns budget status string:
    < 80%: 'Normal'
    80% - 99%: 'Warning'
    >= 100%: 'Exceeded'
    """
    p = float(percentage or 0.0)
    if p >= 100.0:
        return 'Exceeded'
    elif p >= 80.0:
        return 'Warning'
    return 'Normal'

def calculate_goal_progress(current_amount, target_amount):
    """Returns Goal completion percentage = (Current Saved / Target) * 100."""
    target = float(target_amount or 0.0)
    current = float(current_amount or 0.0)
    if target <= 0:
        return 0.0
    progress = (current / target) * 100.0
    return min(round(progress, 1), 100.0)

def calculate_goal_remaining(target_amount, current_amount):
    """Returns Remaining amount to reach goal target."""
    target = float(target_amount or 0.0)
    current = float(current_amount or 0.0)
    rem = target - current
    return max(0.0, round(rem, 2))

def parse_date(date_val):
    if isinstance(date_val, date):
        return date_val
    if isinstance(date_val, datetime):
        return date_val.date()
    return datetime.strptime(str(date_val)[:10], '%Y-%m-%d').date()

def calculate_required_monthly_contribution(target_amount, current_amount, target_date_str, ref_date=None):
    """Calculates monthly contribution needed to reach target by deadline."""
    target = float(target_amount or 0.0)
    current = float(current_amount or 0.0)
    rem_amt = target - current
    if rem_amt <= 0:
        return 0.0

    today = parse_date(ref_date or date.today())
    target_dt = parse_date(target_date_str)

    months_left = (target_dt.year - today.year) * 12 + (target_dt.month - today.month)
    if months_left <= 0:
        return round(rem_amt, 2)

    return round(rem_amt / months_left, 2)

def calculate_expected_goal_progress(start_date_str, target_date_str, ref_date=None):
    """Calculates the expected progress percentage based on elapsed time."""
    start_dt = parse_date(start_date_str)
    target_dt = parse_date(target_date_str)
    today = parse_date(ref_date or date.today())

    total_days = (target_dt - start_dt).days
    if total_days <= 0:
        return 100.0

    elapsed_days = (today - start_dt).days
    if elapsed_days <= 0:
        return 0.0

    expected = (elapsed_days / total_days) * 100.0
    return min(round(expected, 1), 100.0)

def determine_goal_status(current_amount, target_amount, start_date_str, target_date_str, ref_date=None):
    """
    Determines goal status based on saved vs target and expected timeline.
    Statuses: 'Completed', 'Deadline Approaching', 'Behind Schedule', 'On Track', 'In Progress', 'Not Started'
    """
    target = float(target_amount or 0.0)
    current = float(current_amount or 0.0)
    if current >= target and target > 0:
        return 'Completed'

    today = parse_date(ref_date or date.today())
    start_dt = parse_date(start_date_str)
    target_dt = parse_date(target_date_str)

    if today < start_dt and current == 0:
        return 'Not Started'

    days_to_deadline = (target_dt - today).days
    actual_progress = calculate_goal_progress(current, target)
    expected_progress = calculate_expected_goal_progress(start_date_str, target_date_str, today)

    if days_to_deadline <= 30 and days_to_deadline >= 0 and actual_progress < 100:
        return 'Deadline Approaching'
    if actual_progress < (expected_progress - 10.0):
        return 'Behind Schedule'
    if actual_progress >= expected_progress:
        return 'On Track'

    return 'In Progress'

def calculate_monthly_change(current_val, previous_val):
    """Calculates percentage change between two monthly values."""
    curr = float(current_val or 0.0)
    prev = float(previous_val or 0.0)
    if prev == 0:
        return 100.0 if curr > 0 else 0.0
    change = ((curr - prev) / abs(prev)) * 100.0
    return round(change, 1)
