"""
Unit Tests for Repository Layer (Part B - Layered Architecture).
Tests the isolated data access methods for:
- TransactionRepository
- BudgetRepository
- CategoryRepository
"""
import pytest
from repositories.transaction_repository import TransactionRepository
from repositories.budget_repository import BudgetRepository
from repositories.category_repository import CategoryRepository

@pytest.fixture
def repos(app):
    """Provides initialized repository instances within application context."""
    with app.app_context():
        return {
            'tx': TransactionRepository(),
            'budget': BudgetRepository(),
            'cat': CategoryRepository()
        }

def test_category_repository(repos, auth_client):
    cat_repo = repos['cat']
    user_id = 1

    cats = cat_repo.get_all(user_id=user_id, category_type='expense')
    assert len(cats) > 0
    first_cat = cats[0]

    fetched = cat_repo.get_by_id(user_id, first_cat['id'])
    assert fetched is not None
    assert fetched['name'] == first_cat['name']

    by_name = cat_repo.get_by_name_and_type(user_id, first_cat['name'], 'expense')
    assert by_name is not None
    assert by_name['id'] == first_cat['id']

def test_transaction_repository_crud_and_spending(repos, auth_client):
    tx_repo = repos['tx']
    cat_repo = repos['cat']
    user_id = 1

    cats = cat_repo.get_all(user_id=user_id, category_type='expense')
    cat_id = cats[0]['id']

    # 1. Create
    tx_id = tx_repo.create(
        user_id=user_id,
        category_id=cat_id,
        transaction_type='expense',
        amount=2500.0,
        description='Groceries Store',
        transaction_date='2026-10-15',
        payment_method='Credit Card',
        notes='Weekly supplies'
    )
    assert tx_id > 0

    # 2. Get by ID
    tx = tx_repo.get_by_id(user_id, tx_id)
    assert tx is not None
    assert tx['amount'] == 2500.0
    assert tx['payment_method'] == 'Credit Card'
    assert tx['notes'] == 'Weekly supplies'

    # 3. Monthly Spending calculation in repository
    spending = tx_repo.get_monthly_spending(user_id, month=10, year=2026)
    assert spending == 2500.0

    cat_spending = tx_repo.get_category_monthly_spending(user_id, cat_id, month=10, year=2026)
    assert cat_spending == 2500.0

    # 4. Update
    tx_repo.update(user_id, tx_id, {'amount': 3000.0, 'notes': 'Updated supplies'})
    updated = tx_repo.get_by_id(user_id, tx_id)
    assert updated['amount'] == 3000.0
    assert updated['notes'] == 'Updated supplies'

    # 5. Find All
    res = tx_repo.find_all(user_id=user_id, transaction_type='expense', month=10, year=2026)
    assert res['total'] >= 1
    assert any(item['id'] == tx_id for item in res['items'])

    # 6. Delete
    tx_repo.delete(user_id, tx_id)
    assert tx_repo.get_by_id(user_id, tx_id) is None

def test_budget_repository_crud(repos, auth_client):
    b_repo = repos['budget']
    cat_repo = repos['cat']
    user_id = 1

    cats = cat_repo.get_all(user_id=user_id, category_type='expense')
    cat_id = cats[0]['id']

    # 1. Upsert Overall Budget
    ov_id = b_repo.upsert_overall_budget(user_id, month=11, year=2026, amount=60000.0)
    assert ov_id > 0

    ov = b_repo.get_overall_budget(user_id, month=11, year=2026)
    assert ov is not None
    assert ov['amount'] == 60000.0

    # 2. Update Overall Budget (upsert existing)
    b_repo.upsert_overall_budget(user_id, month=11, year=2026, amount=65000.0)
    ov_updated = b_repo.get_overall_budget(user_id, month=11, year=2026)
    assert ov_updated['amount'] == 65000.0

    # 3. Upsert Category Budget
    cat_b_id = b_repo.upsert_category_budget(user_id, category_id=cat_id, month=11, year=2026, amount=15000.0)
    assert cat_b_id > 0

    cat_budgets = b_repo.get_category_budgets(user_id, month=11, year=2026)
    assert len(cat_budgets) == 1
    assert cat_budgets[0]['amount'] == 15000.0

    # 4. Yearly budgets
    yearly = b_repo.get_annual_overall_budgets(user_id, year=2026)
    assert len(yearly) >= 1

    # 5. Delete
    b_repo.delete(user_id, cat_b_id)
    assert b_repo.get_by_id(user_id, cat_b_id) is None
