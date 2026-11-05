"""
Transaction Service (Layered Architecture - Part B).
Contains application & business logic, validation, and domain coordination.
Delegates all database access exclusively to TransactionRepository and CategoryRepository.
No SQL is executed directly in this service layer.
"""
from repositories.transaction_repository import TransactionRepository
from repositories.category_repository import CategoryRepository
from utils.validators import is_valid_date, is_positive_number, sanitize_string

class TransactionService:
    def __init__(self, transaction_repo=None, category_repo=None):
        self.transaction_repo = transaction_repo or TransactionRepository()
        self.category_repo = category_repo or CategoryRepository()

    def add_transaction(self, user_id, category_id, transaction_type, amount, description, transaction_date, payment_method='Cash', notes=''):
        """
        Coordinates business validation and calls the repository to persist the transaction.
        Enforces Controller -> Service -> Repository dependency flow.
        """
        transaction_type = sanitize_string(transaction_type).lower()
        description = sanitize_string(description)
        transaction_date = sanitize_string(transaction_date)
        payment_method = sanitize_string(payment_method) or 'Cash'
        notes = sanitize_string(notes) or ''

        # Business Rule 1: Valid type
        if transaction_type not in ('income', 'expense'):
            return False, "Transaction type must be 'income' or 'expense'."

        # Business Rule 2: Amount must be positive
        if not is_positive_number(amount):
            return False, "Amount must be greater than zero."

        # Business Rule 3: Valid date format
        if not is_valid_date(transaction_date):
            return False, "Invalid transaction date. Use YYYY-MM-DD format."

        # Business Rule 4: Category ownership and type matching
        category = self.category_repo.get_by_id(user_id, category_id)
        if not category:
            return False, "Invalid category selected."
        if category['type'] != transaction_type:
            return False, f"Category '{category['name']}' is a {category['type']} category, cannot be used for {transaction_type}."

        # Delegate persistence to repository layer
        tx_id = self.transaction_repo.create(
            user_id=user_id,
            category_id=category_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            transaction_date=transaction_date,
            payment_method=payment_method,
            notes=notes
        )
        return True, self.transaction_repo.get_by_id(user_id, tx_id)

    def update_transaction(self, user_id, transaction_id, category_id=None, amount=None, description=None, transaction_date=None, payment_method=None, notes=None):
        """Validates updates and delegates persistence to repository."""
        tx = self.transaction_repo.get_by_id(user_id, transaction_id)
        if not tx:
            return False, "Transaction not found or access denied."

        fields_to_update = {}

        if category_id is not None:
            category = self.category_repo.get_by_id(user_id, category_id)
            if not category:
                return False, "Invalid category selected."
            if category['type'] != tx['transaction_type']:
                return False, f"Category '{category['name']}' is a {category['type']} category."
            fields_to_update['category_id'] = category_id

        if amount is not None:
            if not is_positive_number(amount):
                return False, "Amount must be greater than zero."
            fields_to_update['amount'] = float(amount)

        if description is not None:
            fields_to_update['description'] = sanitize_string(description)

        if transaction_date is not None:
            if not is_valid_date(transaction_date):
                return False, "Invalid transaction date format."
            fields_to_update['transaction_date'] = sanitize_string(transaction_date)

        if payment_method is not None:
            fields_to_update['payment_method'] = sanitize_string(payment_method)

        if notes is not None:
            fields_to_update['notes'] = sanitize_string(notes)

        if not fields_to_update:
            return True, tx

        updated_tx = self.transaction_repo.update(user_id, transaction_id, fields_to_update)
        return True, updated_tx

    def delete_transaction(self, user_id, transaction_id):
        """Verifies existence and ownership, then deletes via repository."""
        tx = self.transaction_repo.get_by_id(user_id, transaction_id)
        if not tx:
            return False, "Transaction not found or access denied."
        self.transaction_repo.delete(user_id, transaction_id)
        return True, "Transaction deleted successfully."

    def get_transaction_by_id(self, user_id, transaction_id):
        return self.transaction_repo.get_by_id(user_id, transaction_id)

    def get_transactions(self, user_id, transaction_type=None, category_id=None, month=None, year=None, search=None, page=1, limit=50, sort_by='transaction_date', order='DESC'):
        return self.transaction_repo.find_all(
            user_id=user_id,
            transaction_type=transaction_type,
            category_id=category_id,
            month=month,
            year=year,
            search=search,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order
        )

# Module-level singleton instance & backward-compatible function proxies
_default_service = TransactionService()

def add_transaction(*args, **kwargs):
    return _default_service.add_transaction(*args, **kwargs)

def update_transaction(*args, **kwargs):
    return _default_service.update_transaction(*args, **kwargs)

def delete_transaction(*args, **kwargs):
    return _default_service.delete_transaction(*args, **kwargs)

def get_transaction_by_id(*args, **kwargs):
    return _default_service.get_transaction_by_id(*args, **kwargs)

def get_transactions(*args, **kwargs):
    return _default_service.get_transactions(*args, **kwargs)
