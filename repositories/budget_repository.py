"""
Budget Repository.
Handles all database queries and persistence operations for Budget records.
Services must delegate database operations to this class.
"""
from repositories.base_repository import BaseRepository

class BudgetRepository(BaseRepository):
    def get_by_id(self, user_id, budget_id):
        """Retrieves a single budget record joined with category name."""
        query = """
            SELECT b.*, c.name as category_name
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.id = ? AND b.user_id = ?
        """
        return self.fetch_one(query, (budget_id, user_id))

    def get_overall_budget(self, user_id, month, year):
        """Retrieves the overall monthly budget (where category_id IS NULL)."""
        query = "SELECT * FROM budgets WHERE user_id = ? AND category_id IS NULL AND month = ? AND year = ?"
        return self.fetch_one(query, (user_id, month, year))

    def get_category_budgets(self, user_id, month, year):
        """Retrieves all category-specific budgets for a given month and year."""
        query = """
            SELECT b.*, c.name as category_name
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.user_id = ? AND b.month = ? AND b.year = ?
            ORDER BY c.name ASC
        """
        return self.fetch_all(query, (user_id, month, year))

    def upsert_overall_budget(self, user_id, month, year, amount):
        """Creates or updates the overall monthly budget."""
        existing = self.get_overall_budget(user_id, month, year)
        if existing:
            self.execute(
                "UPDATE budgets SET amount = ? WHERE id = ?",
                (float(amount), existing['id']), commit=True
            )
            return existing['id']
        else:
            return self.execute(
                "INSERT INTO budgets (user_id, category_id, month, year, amount) VALUES (?, NULL, ?, ?, ?)",
                (user_id, month, year, float(amount)), commit=True
            )

    def upsert_category_budget(self, user_id, category_id, month, year, amount):
        """Creates or updates a category-specific budget."""
        query = "SELECT id FROM budgets WHERE user_id = ? AND category_id = ? AND month = ? AND year = ?"
        existing = self.fetch_one(query, (user_id, category_id, month, year))
        if existing:
            self.execute(
                "UPDATE budgets SET amount = ? WHERE id = ?",
                (float(amount), existing['id']), commit=True
            )
            return existing['id']
        else:
            return self.execute(
                "INSERT INTO budgets (user_id, category_id, month, year, amount) VALUES (?, ?, ?, ?, ?)",
                (user_id, category_id, month, year, float(amount)), commit=True
            )

    def delete(self, user_id, budget_id):
        """Deletes a budget record."""
        query = "DELETE FROM budgets WHERE id = ? AND user_id = ?"
        self.execute(query, (budget_id, user_id), commit=True)
        return True

    def get_yearly_budgets(self, user_id, year):
        """Retrieves all monthly budgets for a specific year."""
        query = """
            SELECT b.*, c.name as category_name
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.user_id = ? AND b.year = ?
            ORDER BY b.month ASC
        """
        return self.fetch_all(query, (user_id, year))

    def get_annual_overall_budgets(self, user_id, year):
        """Retrieves overall monthly budgets across all months for a year."""
        query = "SELECT month, amount FROM budgets WHERE user_id = ? AND category_id IS NULL AND year = ?"
        return self.fetch_all(query, (user_id, year))

    def get_annual_category_budgets(self, user_id, year):
        """Retrieves aggregated category-level annual budgets and spending."""
        query = """
            SELECT c.id as category_id, c.name as category_name,
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
            ORDER BY c.name ASC
        """
        return self.fetch_all(query, (year, year, user_id))
