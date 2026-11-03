from datetime import date
from database.database import execute_query, get_db
from utils.calculations import (
    calculate_goal_progress,
    calculate_goal_remaining,
    calculate_required_monthly_contribution,
    calculate_expected_goal_progress,
    determine_goal_status
)
from utils.validators import is_valid_date, is_positive_number, is_non_negative_number, sanitize_string

def add_goal(user_id, goal_name, start_date, target_date, target_amount, starting_amount=0.0, monthly_target=0.0, priority='Medium', notes=''):
    goal_name = sanitize_string(goal_name)
    start_date = sanitize_string(start_date)
    target_date = sanitize_string(target_date)
    priority = sanitize_string(priority) or 'Medium'
    notes = sanitize_string(notes)

    if not goal_name:
        return False, "Goal name cannot be empty."
    if not is_valid_date(start_date) or not is_valid_date(target_date):
        return False, "Invalid start date or target date format (YYYY-MM-DD)."
    if target_date <= start_date:
        return False, "Target deadline date must be after the start date."
    if not is_positive_number(target_amount):
        return False, "Target amount must be greater than zero."
    if not is_non_negative_number(starting_amount):
        return False, "Starting amount cannot be negative."

    target_amt = float(target_amount)
    start_amt = float(starting_amount)
    if start_amt > target_amt:
        return False, "Starting amount cannot exceed target amount."

    current_amt = start_amt
    m_target = float(monthly_target) if is_non_negative_number(monthly_target) else calculate_required_monthly_contribution(target_amt, current_amt, target_date)
    status = determine_goal_status(current_amt, target_amt, start_date, target_date)

    goal_id = execute_query(
        """INSERT INTO goals (user_id, goal_name, start_date, target_date, target_amount, starting_amount,
           current_amount, monthly_target, priority, status, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, goal_name, start_date, target_date, target_amt, start_amt, current_amt, m_target, priority, status, notes),
        commit=True
    )

    return True, get_goal_by_id(user_id, goal_id)

def update_goal(user_id, goal_id, goal_name=None, start_date=None, target_date=None, target_amount=None, starting_amount=None, monthly_target=None, priority=None, notes=None):
    goal = get_goal_by_id(user_id, goal_id)
    if not goal:
        return False, "Goal not found or access denied."

    updates = []
    params = []

    s_dt = goal['start_date']
    t_dt = goal['target_date']
    t_amt = goal['target_amount']
    st_amt = goal['starting_amount']
    c_amt = goal['current_amount']

    if goal_name is not None:
        g_name = sanitize_string(goal_name)
        if not g_name:
            return False, "Goal name cannot be empty."
        updates.append("goal_name = ?")
        params.append(g_name)

    if start_date is not None:
        if not is_valid_date(start_date):
            return False, "Invalid start date format."
        s_dt = sanitize_string(start_date)
        updates.append("start_date = ?")
        params.append(s_dt)

    if target_date is not None:
        if not is_valid_date(target_date):
            return False, "Invalid target date format."
        t_dt = sanitize_string(target_date)
        updates.append("target_date = ?")
        params.append(t_dt)

    if target_amount is not None:
        if not is_positive_number(target_amount):
            return False, "Target amount must be positive."
        t_amt = float(target_amount)
        updates.append("target_amount = ?")
        params.append(t_amt)

    if starting_amount is not None:
        if not is_non_negative_number(starting_amount):
            return False, "Starting amount cannot be negative."
        st_amt = float(starting_amount)
        updates.append("starting_amount = ?")
        params.append(st_amt)

    if t_dt <= s_dt:
        return False, "Target date must be after start date."

    if monthly_target is not None and is_non_negative_number(monthly_target):
        updates.append("monthly_target = ?")
        params.append(float(monthly_target))

    if priority is not None:
        updates.append("priority = ?")
        params.append(sanitize_string(priority))

    if notes is not None:
        updates.append("notes = ?")
        params.append(sanitize_string(notes))

    # Recalculate status
    new_status = determine_goal_status(c_amt, t_amt, s_dt, t_dt)
    updates.append("status = ?")
    params.append(new_status)

    params.extend([goal_id, user_id])
    query = f"UPDATE goals SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
    execute_query(query, params, commit=True)

    return True, get_goal_by_id(user_id, goal_id)

def delete_goal(user_id, goal_id):
    goal = get_goal_by_id(user_id, goal_id)
    if not goal:
        return False, "Goal not found or access denied."
    execute_query("DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_id), commit=True)
    return True, "Goal deleted successfully."

def get_goal_by_id(user_id, goal_id):
    query = "SELECT * FROM goals WHERE id = ? AND user_id = ?"
    goal = execute_query(query, (goal_id, user_id), fetch_one=True)
    if not goal:
        return None
    return format_goal_details(goal)

def format_goal_details(goal):
    target = float(goal['target_amount'])
    current = float(goal['current_amount'])
    start_dt = goal['start_date']
    target_dt = goal['target_date']

    progress = calculate_goal_progress(current, target)
    remaining = calculate_goal_remaining(target, current)
    req_monthly = calculate_required_monthly_contribution(target, current, target_dt)
    expected_progress = calculate_expected_goal_progress(start_dt, target_dt)
    status = determine_goal_status(current, target, start_dt, target_dt)

    return {
        'id': goal['id'],
        'user_id': goal['user_id'],
        'goal_name': goal['goal_name'],
        'start_date': start_dt,
        'target_date': target_dt,
        'target_amount': target,
        'starting_amount': float(goal['starting_amount']),
        'current_amount': current,
        'monthly_target': float(goal['monthly_target']),
        'required_monthly': req_monthly,
        'priority': goal['priority'],
        'status': status,
        'notes': goal['notes'],
        'remaining_amount': remaining,
        'progress_percentage': progress,
        'expected_progress_percentage': expected_progress,
        'created_at': goal['created_at']
    }

def get_goals(user_id):
    query = "SELECT * FROM goals WHERE user_id = ? ORDER BY target_date ASC, priority DESC"
    raw_goals = execute_query(query, (user_id,))
    goals = [format_goal_details(g) for g in raw_goals]

    tot_target = sum(g['target_amount'] for g in goals)
    tot_saved = sum(g['current_amount'] for g in goals)
    tot_starting = sum(g['starting_amount'] for g in goals)
    active_goals = [g for g in goals if g['status'] != 'Completed']
    completed_goals = [g for g in goals if g['status'] == 'Completed']

    overall_progress = calculate_goal_progress(tot_saved, tot_target) if tot_target > 0 else 0.0

    return {
        'goals': goals,
        'summary': {
            'total_goal_amount': tot_target,
            'total_starting_amount': tot_starting,
            'total_saved_amount': tot_saved,
            'active_goals_count': len(active_goals),
            'completed_goals_count': len(completed_goals),
            'overall_progress_percentage': overall_progress
        }
    }

def add_goal_contribution(user_id, goal_id, amount, contribution_date=None, description=''):
    goal = get_goal_by_id(user_id, goal_id)
    if not goal:
        return False, "Goal not found or access denied."

    if not is_positive_number(amount):
        return False, "Contribution amount must be greater than zero."

    contrib_date = sanitize_string(contribution_date) or date.today().strftime('%Y-%m-%d')
    if not is_valid_date(contrib_date):
        return False, "Invalid contribution date format."

    amt = float(amount)
    new_current = goal['current_amount'] + amt

    with get_db() as conn:
        conn.execute(
            "INSERT INTO goal_contributions (goal_id, amount, contribution_date, description) VALUES (?, ?, ?, ?)",
            (goal_id, amt, contrib_date, sanitize_string(description))
        )
        new_status = determine_goal_status(new_current, goal['target_amount'], goal['start_date'], goal['target_date'])
        conn.execute(
            "UPDATE goals SET current_amount = ?, status = ? WHERE id = ?",
            (new_current, new_status, goal_id)
        )

    return True, get_goal_by_id(user_id, goal_id)

def delete_goal_contribution(user_id, contribution_id):
    query = """
        SELECT gc.*, g.id as goal_id, g.user_id, g.current_amount, g.target_amount, g.start_date, g.target_date
        FROM goal_contributions gc
        JOIN goals g ON gc.goal_id = g.id
        WHERE gc.id = ? AND g.user_id = ?
    """
    contrib = execute_query(query, (contribution_id, user_id), fetch_one=True)
    if not contrib:
        return False, "Contribution record not found or access denied."

    goal_id = contrib['goal_id']
    amt = float(contrib['amount'])
    new_current = max(0.0, float(contrib['current_amount']) - amt)

    with get_db() as conn:
        conn.execute("DELETE FROM goal_contributions WHERE id = ?", (contribution_id,))
        new_status = determine_goal_status(new_current, contrib['target_amount'], contrib['start_date'], contrib['target_date'])
        conn.execute("UPDATE goals SET current_amount = ?, status = ? WHERE id = ?", (new_current, new_status, goal_id))

    return True, get_goal_by_id(user_id, goal_id)

def get_goal_contributions(user_id, goal_id):
    goal = get_goal_by_id(user_id, goal_id)
    if not goal:
        return None
    query = "SELECT * FROM goal_contributions WHERE goal_id = ? ORDER BY contribution_date DESC, id DESC"
    contributions = execute_query(query, (goal_id,))
    return {
        'goal': goal,
        'contributions': contributions
    }

def get_goal_alerts(user_id):
    goals_data = get_goals(user_id)
    alerts = []

    for g in goals_data['goals']:
        if g['status'] == 'Completed':
            alerts.append({
                'type': 'success',
                'title': f"Goal Completed: {g['goal_name']}",
                'message': f"Congratulations! You reached 100% of your target for '{g['goal_name']}'."
            })
        elif g['status'] == 'Deadline Approaching':
            alerts.append({
                'type': 'warning',
                'title': f"Deadline Approaching: {g['goal_name']}",
                'message': f"Goal '{g['goal_name']}' target date ({g['target_date']}) is approaching soon. You have saved {g['progress_percentage']}%."
            })
        elif g['status'] == 'Behind Schedule':
            alerts.append({
                'type': 'danger',
                'title': f"Behind Schedule: {g['goal_name']}",
                'message': f"Goal '{g['goal_name']}' is currently behind target trajectory. Target: Rs. {g['target_amount']:,.2f}, Saved: Rs. {g['current_amount']:,.2f}."
            })

    return alerts
