"""
Base Repository for ExpenseMate.
Encapsulates database access utilities so that repositories are the sole
layer responsible for SQL execution.
"""
from database.database import execute_query, get_db

class BaseRepository:
    def execute(self, query, params=(), commit=False):
        """Executes a parameterized SQL query with commit if needed."""
        return execute_query(query, params, commit=commit)

    def fetch_one(self, query, params=()):
        """Executes query and returns a single row as a dictionary, or None."""
        return execute_query(query, params, fetch_one=True)

    def fetch_all(self, query, params=()):
        """Executes query and returns all matching rows as dictionaries."""
        return execute_query(query, params, fetch_all=True)
