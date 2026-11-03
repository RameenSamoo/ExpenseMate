import csv
import io
from database.database import execute_query, get_db
from utils.validators import is_valid_date, is_positive_number, sanitize_string
from services.category_service import add_category

def export_transactions_csv(user_id, transaction_type=None, category_id=None, month=None, year=None):
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

    where_sql = " WHERE " + " AND ".join(where_clauses)
    query = f"""
        SELECT t.transaction_date as Date,
               t.transaction_type as Type,
               c.name as Category,
               t.amount as Amount,
               t.description as Description
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        {where_sql}
        ORDER BY t.transaction_date DESC, t.id DESC
    """
    rows = execute_query(query, params)

    output = io.StringIO()
    # Add UTF-8 BOM (\ufeff) so Microsoft Excel opens the CSV cleanly without corrupted date encoding or '##' column errors
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description'])

    for row in rows:
        # Standardize date format to YYYY-MM-DD
        date_str = str(row['Date'])[:10] if row['Date'] else ''
        writer.writerow([
            date_str,
            row['Type'],
            row['Category'],
            row['Amount'],
            row['Description'] or ''
        ])

    return output.getvalue()

def import_transactions_csv(user_id, csv_text):
    if not csv_text or not csv_text.strip():
        return False, "CSV content is empty."

    f = io.StringIO(csv_text.strip())
    reader = csv.DictReader(f)

    if not reader.fieldnames:
        return False, "CSV header is missing or empty."

    # Standardize header names
    field_map = {name.strip().lower(): name for name in reader.fieldnames}
    required_cols = ['date', 'type', 'category', 'amount']
    missing_cols = [c for c in required_cols if c not in field_map]
    if missing_cols:
        return False, f"Missing required columns in CSV: {', '.join(missing_cols)}"

    # Get user's existing categories mapping
    cats = execute_query("SELECT id, name, type FROM categories WHERE user_id = ?", (user_id,))
    cat_lookup = {(c['name'].strip().lower(), c['type'].strip().lower()): c['id'] for c in cats}

    imported_count = 0
    rejected_count = 0
    errors = []

    row_num = 1
    with get_db() as conn:
        for row in reader:
            row_num += 1
            raw_date = sanitize_string(row.get(field_map['date']))
            raw_type = sanitize_string(row.get(field_map['type'])).lower()
            raw_cat = sanitize_string(row.get(field_map['category']))
            raw_amt = sanitize_string(row.get(field_map['amount']))
            raw_desc = sanitize_string(row.get(field_map.get('description', '')))

            row_errors = []
            if not is_valid_date(raw_date):
                row_errors.append(f"Row {row_num}: Invalid date '{raw_date}' (expected YYYY-MM-DD).")
            if raw_type not in ('income', 'expense'):
                row_errors.append(f"Row {row_num}: Invalid type '{raw_type}' (expected 'income' or 'expense').")
            if not is_positive_number(raw_amt):
                row_errors.append(f"Row {row_num}: Invalid amount '{raw_amt}'. Must be positive number.")

            if row_errors:
                rejected_count += 1
                errors.extend(row_errors)
                continue

            # Check or create category
            cat_key = (raw_cat.lower(), raw_type)
            cat_id = cat_lookup.get(cat_key)
            if not cat_id:
                # Auto-create category if missing
                cur = conn.execute(
                    "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)",
                    (user_id, raw_cat, raw_type)
                )
                cat_id = cur.lastrowid
                cat_lookup[cat_key] = cat_id

            conn.execute(
                """INSERT INTO transactions (user_id, category_id, transaction_type, amount, description, transaction_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, cat_id, raw_type, float(raw_amt), raw_desc, raw_date)
            )
            imported_count += 1

    return True, {
        'imported': imported_count,
        'rejected': rejected_count,
        'errors': errors
    }
