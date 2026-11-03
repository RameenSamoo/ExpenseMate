from database.database import execute_query
from utils.validators import sanitize_string

def get_user_categories(user_id, category_type=None):
    if category_type:
        query = "SELECT * FROM categories WHERE user_id = ? AND type = ? ORDER BY name ASC"
        return execute_query(query, (user_id, category_type))
    query = "SELECT * FROM categories WHERE user_id = ? ORDER BY type DESC, name ASC"
    return execute_query(query, (user_id,))

def add_category(user_id, name, category_type):
    name = sanitize_string(name)
    category_type = sanitize_string(category_type).lower()

    if not name:
        return False, "Category name cannot be empty."
    if category_type not in ('income', 'expense'):
        return False, "Category type must be 'income' or 'expense'."

    existing = execute_query(
        "SELECT id FROM categories WHERE user_id = ? AND LOWER(name) = LOWER(?) AND type = ?",
        (user_id, name, category_type), fetch_one=True
    )
    if existing:
        return False, f"A {category_type} category named '{name}' already exists."

    cat_id = execute_query(
        "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)",
        (user_id, name, category_type), commit=True
    )
    category = execute_query("SELECT * FROM categories WHERE id = ?", (cat_id,), fetch_one=True)
    return True, category

def update_category(user_id, category_id, new_name):
    new_name = sanitize_string(new_name)
    if not new_name:
        return False, "Category name cannot be empty."

    category = execute_query("SELECT * FROM categories WHERE id = ? AND user_id = ?", (category_id, user_id), fetch_one=True)
    if not category:
        return False, "Category not found or access denied."

    existing = execute_query(
        "SELECT id FROM categories WHERE user_id = ? AND LOWER(name) = LOWER(?) AND type = ? AND id != ?",
        (user_id, new_name, category['type'], category_id), fetch_one=True
    )
    if existing:
        return False, f"Another {category['type']} category named '{new_name}' already exists."

    execute_query("UPDATE categories SET name = ? WHERE id = ?", (new_name, category_id), commit=True)
    updated = execute_query("SELECT * FROM categories WHERE id = ?", (category_id,), fetch_one=True)
    return True, updated

def delete_category(user_id, category_id):
    category = execute_query("SELECT * FROM categories WHERE id = ? AND user_id = ?", (category_id, user_id), fetch_one=True)
    if not category:
        return False, "Category not found or access denied."

    # Safeguard check: transactions
    tx_count = execute_query(
        "SELECT COUNT(*) as cnt FROM transactions WHERE category_id = ? AND user_id = ?",
        (category_id, user_id), fetch_one=True
    )
    if tx_count and tx_count['cnt'] > 0:
        return False, f"Cannot delete category '{category['name']}' because {tx_count['cnt']} transaction(s) depend on it."

    # Safeguard check: budgets
    b_count = execute_query(
        "SELECT COUNT(*) as cnt FROM budgets WHERE category_id = ? AND user_id = ?",
        (category_id, user_id), fetch_one=True
    )
    if b_count and b_count['cnt'] > 0:
        return False, f"Cannot delete category '{category['name']}' because budget limits are assigned to it."

    execute_query("DELETE FROM categories WHERE id = ? AND user_id = ?", (category_id, user_id), commit=True)
    return True, "Category deleted successfully."
