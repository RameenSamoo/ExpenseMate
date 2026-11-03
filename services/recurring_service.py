from database.database import execute_query
from utils.validators import is_valid_date, is_positive_number, sanitize_string

def get_recurring_expenses(user_id):
    query = """
        SELECT r.*, c.name as category_name
        FROM recurring_expenses r
        JOIN categories c ON r.category_id = c.id
        WHERE r.user_id = ?
        ORDER BY r.name ASC
    """
    return execute_query(query, (user_id,))

def add_recurring_expense(user_id, name, category_id, amount, frequency, start_date, end_date=None):
    name = sanitize_string(name)
    frequency = sanitize_string(frequency).lower()
    start_date = sanitize_string(start_date)
    end_date = sanitize_string(end_date) if end_date else None

    if not name:
        return False, "Recurring bill name cannot be empty."
    if frequency not in ('daily', 'weekly', 'monthly', 'yearly'):
        return False, "Frequency must be daily, weekly, monthly, or yearly."
    if not is_positive_number(amount):
        return False, "Amount must be greater than zero."
    if not is_valid_date(start_date):
        return False, "Invalid start date format."
    if end_date and not is_valid_date(end_date):
        return False, "Invalid end date format."

    category = execute_query("SELECT * FROM categories WHERE id = ? AND user_id = ? AND type = 'expense'", (category_id, user_id), fetch_one=True)
    if not category:
        return False, "Invalid expense category selected."

    r_id = execute_query(
        """INSERT INTO recurring_expenses (user_id, name, category_id, amount, frequency, start_date, end_date)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, name, category_id, float(amount), frequency, start_date, end_date),
        commit=True
    )
    return True, get_recurring_by_id(user_id, r_id)

def get_recurring_by_id(user_id, recurring_id):
    query = """
        SELECT r.*, c.name as category_name
        FROM recurring_expenses r
        JOIN categories c ON r.category_id = c.id
        WHERE r.id = ? AND r.user_id = ?
    """
    return execute_query(query, (recurring_id, user_id), fetch_one=True)

def delete_recurring_expense(user_id, recurring_id):
    item = get_recurring_by_id(user_id, recurring_id)
    if not item:
        return False, "Recurring expense not found or access denied."
    execute_query("DELETE FROM recurring_expenses WHERE id = ? AND user_id = ?", (recurring_id, user_id), commit=True)
    return True, "Recurring expense deleted successfully."
