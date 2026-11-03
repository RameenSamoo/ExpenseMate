from werkzeug.security import generate_password_hash, check_password_hash
from database.database import execute_query, get_db
from database.seed import seed_default_categories
from utils.validators import is_valid_email, is_valid_password, sanitize_string

def register_user(full_name, email, password, confirm_password):
    full_name = sanitize_string(full_name)
    email = sanitize_string(email).lower()

    if not full_name:
        return False, "Full name cannot be empty."
    if not is_valid_email(email):
        return False, "Invalid email address format."
    if not is_valid_password(password, min_length=6):
        return False, "Password must be at least 6 characters long."
    if password != confirm_password:
        return False, "Passwords do not match."

    # Check email uniqueness
    existing = execute_query("SELECT id FROM users WHERE email = ?", (email,), fetch_one=True)
    if existing:
        return False, "An account with this email already exists."

    pwd_hash = generate_password_hash(password)

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (full_name, email, password_hash, currency) VALUES (?, ?, ?, 'PKR')",
            (full_name, email, pwd_hash)
        )
        user_id = cursor.lastrowid
        seed_default_categories(conn, user_id)

    user = get_user_by_id(user_id)
    return True, user

def login_user(email, password):
    email = sanitize_string(email).lower()
    if not email or not password:
        return False, "Email and password are required."

    user = execute_query("SELECT * FROM users WHERE email = ?", (email,), fetch_one=True)
    if not user or not check_password_hash(user['password_hash'], password):
        return False, "Invalid email or password."

    return True, {
        'id': user['id'],
        'full_name': user['full_name'],
        'email': user['email'],
        'currency': user['currency']
    }

def get_user_by_id(user_id):
    user = execute_query("SELECT id, full_name, email, currency, created_at FROM users WHERE id = ?", (user_id,), fetch_one=True)
    return user

def update_user_profile(user_id, full_name=None, email=None, currency=None, current_password=None, new_password=None):
    user = execute_query("SELECT * FROM users WHERE id = ?", (user_id,), fetch_one=True)
    if not user:
        return False, "User not found."

    updates = []
    params = []

    if full_name is not None:
        full_name = sanitize_string(full_name)
        if not full_name:
            return False, "Full name cannot be empty."
        updates.append("full_name = ?")
        params.append(full_name)

    if email is not None:
        email = sanitize_string(email).lower()
        if not is_valid_email(email):
            return False, "Invalid email address format."
        existing = execute_query("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id), fetch_one=True)
        if existing:
            return False, "Email is already taken by another account."
        updates.append("email = ?")
        params.append(email)

    if currency is not None:
        currency = sanitize_string(currency)
        if currency:
            updates.append("currency = ?")
            params.append(currency)

    if new_password:
        if not current_password or not check_password_hash(user['password_hash'], current_password):
            return False, "Current password is incorrect."
        if not is_valid_password(new_password, min_length=6):
            return False, "New password must be at least 6 characters long."
        updates.append("password_hash = ?")
        params.append(generate_password_hash(new_password))

    if not updates:
        return True, "No changes made."

    params.append(user_id)
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
    execute_query(query, params, commit=True)
    return True, get_user_by_id(user_id)
