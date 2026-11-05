from database.database import execute_query
from utils.validators import is_valid_date, is_positive_number, sanitize_string

def add_transaction(user_id, category_id, transaction_type, amount, description, transaction_date, payment_method='Cash', notes=''):
    transaction_type = sanitize_string(transaction_type).lower()
    description = sanitize_string(description)
    transaction_date = sanitize_string(transaction_date)
    payment_method = sanitize_string(payment_method) or 'Cash'
    notes = sanitize_string(notes) or ''

    if transaction_type not in ('income', 'expense'):
        return False, "Transaction type must be 'income' or 'expense'."
    if not is_positive_number(amount):
        return False, "Amount must be greater than zero."
    if not is_valid_date(transaction_date):
        return False, "Invalid transaction date. Use YYYY-MM-DD format."

    # Validate category ownership and type match
    category = execute_query(
        "SELECT * FROM categories WHERE id = ? AND user_id = ?",
        (category_id, user_id), fetch_one=True
    )
    if not category:
        return False, "Invalid category selected."
    if category['type'] != transaction_type:
        return False, f"Category '{category['name']}' is a {category['type']} category, cannot be used for {transaction_type}."

    tx_id = execute_query(
        """INSERT INTO transactions (user_id, category_id, transaction_type, amount, description, transaction_date, payment_method, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, category_id, transaction_type, float(amount), description, transaction_date, payment_method, notes),
        commit=True
    )
    return True, get_transaction_by_id(user_id, tx_id)

def update_transaction(user_id, transaction_id, category_id=None, amount=None, description=None, transaction_date=None, payment_method=None, notes=None):
    tx = get_transaction_by_id(user_id, transaction_id)
    if not tx:
        return False, "Transaction not found or access denied."

    updates = []
    params = []

    if category_id is not None:
        category = execute_query(
            "SELECT * FROM categories WHERE id = ? AND user_id = ?",
            (category_id, user_id), fetch_one=True
        )
        if not category:
            return False, "Invalid category selected."
        if category['type'] != tx['transaction_type']:
            return False, f"Category '{category['name']}' is a {category['type']} category."
        updates.append("category_id = ?")
        params.append(category_id)

    if amount is not None:
        if not is_positive_number(amount):
            return False, "Amount must be greater than zero."
        updates.append("amount = ?")
        params.append(float(amount))

    if description is not None:
        updates.append("description = ?")
        params.append(sanitize_string(description))

    if transaction_date is not None:
        if not is_valid_date(transaction_date):
            return False, "Invalid transaction date format."
        updates.append("transaction_date = ?")
        params.append(sanitize_string(transaction_date))

    if payment_method is not None:
        updates.append("payment_method = ?")
        params.append(sanitize_string(payment_method))

    if notes is not None:
        updates.append("notes = ?")
        params.append(sanitize_string(notes))

    if not updates:
        return True, tx

    params.append(transaction_id)
    params.append(user_id)

    query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
    execute_query(query, params, commit=True)
    return True, get_transaction_by_id(user_id, transaction_id)

def delete_transaction(user_id, transaction_id):
    tx = get_transaction_by_id(user_id, transaction_id)
    if not tx:
        return False, "Transaction not found or access denied."

    execute_query("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id), commit=True)
    return True, "Transaction deleted successfully."

def get_transaction_by_id(user_id, transaction_id):
    query = """
        SELECT t.*, c.name as category_name, c.type as category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.id = ? AND t.user_id = ?
    """
    return execute_query(query, (transaction_id, user_id), fetch_one=True)

def get_transactions(user_id, transaction_type=None, category_id=None, month=None, year=None, search=None, page=1, limit=50, sort_by='transaction_date', order='DESC'):
    where_clauses = ["t.user_id = ?"]
    params = [user_id]

    if transaction_type in ('income', 'expense'):
        where_clauses.append("t.transaction_type = ?")
        params.append(transaction_type)

    if category_id:
        where_clauses.append("t.category_id = ?")
        params.append(category_id)

    if month:
        where_clauses.append("CAST(strftime('%m', t.transaction_date) AS INTEGER) = ?")
        params.append(int(month))

    if year:
        where_clauses.append("CAST(strftime('%Y', t.transaction_date) AS INTEGER) = ?")
        params.append(int(year))

    if search:
        where_clauses.append("(t.description LIKE ? OR c.name LIKE ?)")
        search_term = f"%{search.strip()}%"
        params.extend([search_term, search_term])

    where_sql = " WHERE " + " AND ".join(where_clauses)

    # Valid sort columns
    allowed_sorts = {
        'transaction_date': 't.transaction_date',
        'amount': 't.amount',
        'category_name': 'c.name',
        'created_at': 't.created_at'
    }
    sort_column = allowed_sorts.get(sort_by, 't.transaction_date')
    sort_order = 'ASC' if str(order).upper() == 'ASC' else 'DESC'

    count_query = f"SELECT COUNT(*) as total FROM transactions t JOIN categories c ON t.category_id = c.id {where_sql}"
    total_count = execute_query(count_query, params, fetch_one=True)['total']

    offset = (max(1, int(page)) - 1) * int(limit)
    data_query = f"""
        SELECT t.*, c.name as category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        {where_sql}
        ORDER BY {sort_column} {sort_order}, t.id DESC
        LIMIT ? OFFSET ?
    """
    data_params = params + [int(limit), offset]
    items = execute_query(data_query, data_params)

    return {
        'items': items,
        'total': total_count,
        'page': int(page),
        'limit': int(limit),
        'total_pages': max(1, (total_count + int(limit) - 1) // int(limit))
    }
