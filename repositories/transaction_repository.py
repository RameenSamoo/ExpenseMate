"""
Transaction Repository.
Handles all database queries and data persistence operations for Transactions.
Services must delegate database operations to this class.
"""
from repositories.base_repository import BaseRepository

class TransactionRepository(BaseRepository):
    def create(self, user_id, category_id, transaction_type, amount, description, transaction_date, payment_method='Cash', notes=''):
        """Inserts a new transaction record and returns its generated ID."""
        query = """
            INSERT INTO transactions (user_id, category_id, transaction_type, amount, description, transaction_date, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute(
            query,
            (user_id, category_id, transaction_type, float(amount), description, transaction_date, payment_method, notes),
            commit=True
        )

    def get_by_id(self, user_id, transaction_id):
        """Retrieves a single transaction joined with its category information."""
        query = """
            SELECT t.*, c.name as category_name, c.type as category_type
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.id = ? AND t.user_id = ?
        """
        return self.fetch_one(query, (transaction_id, user_id))

    def update(self, user_id, transaction_id, fields_to_update):
        """
        Dynamically updates fields of a transaction record.
        fields_to_update: dict of column_name -> new_value.
        """
        if not fields_to_update:
            return self.get_by_id(user_id, transaction_id)

        set_clauses = [f"{col} = ?" for col in fields_to_update.keys()]
        params = list(fields_to_update.values()) + [transaction_id, user_id]
        query = f"UPDATE transactions SET {', '.join(set_clauses)} WHERE id = ? AND user_id = ?"
        self.execute(query, params, commit=True)
        return self.get_by_id(user_id, transaction_id)

    def delete(self, user_id, transaction_id):
        """Deletes a transaction record belonging to the given user."""
        query = "DELETE FROM transactions WHERE id = ? AND user_id = ?"
        self.execute(query, (transaction_id, user_id), commit=True)
        return True

    def get_monthly_spending(self, user_id, month, year):
        """Calculates total expense spending for a specific month and year."""
        query = """
            SELECT COALESCE(SUM(amount), 0.0) as total
            FROM transactions
            WHERE user_id = ? AND transaction_type = 'expense'
            AND CAST(strftime('%m', transaction_date) AS INTEGER) = ?
            AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?
        """
        row = self.fetch_one(query, (user_id, month, year))
        return float(row['total']) if row and row['total'] is not None else 0.0

    def get_category_monthly_spending(self, user_id, category_id, month, year):
        """Calculates total expense spending for a specific category, month, and year."""
        query = """
            SELECT COALESCE(SUM(amount), 0.0) as total
            FROM transactions
            WHERE user_id = ? AND category_id = ? AND transaction_type = 'expense'
            AND CAST(strftime('%m', transaction_date) AS INTEGER) = ?
            AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?
        """
        row = self.fetch_one(query, (user_id, category_id, month, year))
        return float(row['total']) if row and row['total'] is not None else 0.0

    def get_annual_monthly_expenses(self, user_id, year):
        """Retrieves aggregated expense totals grouped by month for a specific year."""
        query = """
            SELECT CAST(strftime('%m', transaction_date) AS INTEGER) as month_num,
                   COALESCE(SUM(amount), 0.0) as total
            FROM transactions
            WHERE user_id = ? AND transaction_type = 'expense'
            AND CAST(strftime('%Y', transaction_date) AS INTEGER) = ?
            GROUP BY month_num
        """
        return self.fetch_all(query, (user_id, year))

    def find_all(self, user_id, transaction_type=None, category_id=None, month=None, year=None, search=None, page=1, limit=50, sort_by='transaction_date', order='DESC'):
        """Retrieves paginated and filtered transactions for a user."""
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

        allowed_sorts = {
            'transaction_date': 't.transaction_date',
            'amount': 't.amount',
            'category_name': 'c.name',
            'created_at': 't.created_at'
        }
        sort_column = allowed_sorts.get(sort_by, 't.transaction_date')
        sort_order = 'ASC' if str(order).upper() == 'ASC' else 'DESC'

        count_query = f"SELECT COUNT(*) as total FROM transactions t JOIN categories c ON t.category_id = c.id {where_sql}"
        count_row = self.fetch_one(count_query, params)
        total_count = count_row['total'] if count_row else 0

        offset = (max(1, int(page)) - 1) * int(limit)
        data_query = f"""
            SELECT t.*, c.name as category_name
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            {where_sql}
            ORDER BY {sort_column} {sort_order}, t.id DESC
            LIMIT ? OFFSET ?
        """
        items = self.fetch_all(data_query, params + [int(limit), offset])

        return {
            'items': items,
            'total': total_count,
            'page': int(page),
            'limit': int(limit),
            'total_pages': max(1, (total_count + int(limit) - 1) // int(limit))
        }
