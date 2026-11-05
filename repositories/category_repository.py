"""
Category Repository.
Handles all database operations for Category entities.
"""
from repositories.base_repository import BaseRepository

class CategoryRepository(BaseRepository):
    def get_by_id(self, user_id, category_id):
        """Retrieves a single category by user ID and category ID."""
        query = "SELECT * FROM categories WHERE id = ? AND user_id = ?"
        return self.fetch_one(query, (category_id, user_id))

    def get_by_name_and_type(self, user_id, name, category_type):
        """Retrieves a category matching exact name and type for a user."""
        query = "SELECT * FROM categories WHERE user_id = ? AND LOWER(name) = LOWER(?) AND type = ?"
        return self.fetch_one(query, (user_id, name, category_type))

    def get_all(self, user_id, category_type=None):
        """Retrieves all categories for a user, optionally filtered by type."""
        if category_type:
            query = "SELECT * FROM categories WHERE user_id = ? AND type = ? ORDER BY name ASC"
            return self.fetch_all(query, (user_id, category_type))
        query = "SELECT * FROM categories WHERE user_id = ? ORDER BY name ASC"
        return self.fetch_all(query, (user_id,))
