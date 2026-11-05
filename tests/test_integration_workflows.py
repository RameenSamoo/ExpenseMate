"""
Integration & System Test Package (Assignment 02 Engineering Requirements).
Covers 5 end-to-end ExpenseMate workflows:
1. Workflow 1: User Registration, Session Authentication, and Default Category Seeding.
2. Workflow 2: Expense Lifecycle with Migrated Payment Methods and Notes.
3. Workflow 3: Monthly Budget Lifecycle and Multi-tier Status Alerts (Normal -> Warning -> Exceeded).
4. Workflow 4: Savings Goal Creation, Incremental Contributions, and Completion.
5. Workflow 5: Multi-Month Cash Flow Analytics and Month-over-Month Category Comparison.
"""
import pytest

def test_workflow_1_user_lifecycle_and_category_seeding(client):
    """Workflow 1: Register -> Login -> Verify automatic category generation."""
    # Register
    reg_res = client.post('/api/auth/register', json={
        'full_name': 'Workflow User',
        'email': 'workflow_user@expensemate.com',
        'password': 'SecurePassword123!',
        'confirm_password': 'SecurePassword123!'
    })
    assert reg_res.status_code == 201
    assert reg_res.get_json()['success'] is True

    # Login
    login_res = client.post('/api/auth/login', json={
        'email': 'workflow_user@expensemate.com',
        'password': 'SecurePassword123!'
    })
    assert login_res.status_code == 200
    assert login_res.get_json()['success'] is True

    # Check default categories seeded
    cat_res = client.get('/api/categories?type=expense')
    assert cat_res.status_code == 200
    categories = cat_res.get_json()['data']
    assert len(categories) > 0
    cat_names = [c['name'] for c in categories]
    assert any('Food' in name or 'Groceries' in name or 'Bills' in name for name in cat_names)

def test_workflow_2_expense_lifecycle_with_migrated_attributes(auth_client):
    """Workflow 2: Record income -> Record expense with payment_method & notes -> Check Balance."""
    # 1. Fetch Categories
    inc_cats = auth_client.get('/api/categories?type=income').get_json()['data']
    exp_cats = auth_client.get('/api/categories?type=expense').get_json()['data']

    # 2. Record Income
    auth_client.post('/api/income', json={
        'category_id': inc_cats[0]['id'],
        'amount': 80000,
        'transaction_date': '2026-11-01',
        'description': 'Monthly Consultancy',
        'payment_method': 'Bank Transfer',
        'notes': 'Invoice #2026-11'
    })

    # 3. Record Expense with migrated fields
    exp_res = auth_client.post('/api/expenses', json={
        'category_id': exp_cats[0]['id'],
        'amount': 15000,
        'transaction_date': '2026-11-03',
        'description': 'Quarterly Insurance',
        'payment_method': 'Credit Card',
        'notes': 'Policy renewal'
    })
    assert exp_res.status_code == 201
    tx_data = exp_res.get_json()['data']
    assert tx_data['payment_method'] == 'Credit Card'
    assert tx_data['notes'] == 'Policy renewal'

    # 4. Check Dashboard Balance
    dash_res = auth_client.get('/api/dashboard?month=11&year=2026')
    assert dash_res.status_code == 200
    metrics = dash_res.get_json()['data']['metrics']
    assert metrics['total_income'] == 80000.0
    assert metrics['total_expenses'] == 15000.0
    assert metrics['savings'] == 65000.0

def test_workflow_3_monthly_budget_lifecycle_and_warning_trigger(auth_client):
    """Workflow 3: Set Budget -> Add Expenses -> Trigger Warning -> Exceed Budget."""
    exp_cats = auth_client.get('/api/categories?type=expense').get_json()['data']
    food_cat = exp_cats[0]

    # 1. Set Category Budget of 10,000 for Nov 2026
    b_res = auth_client.post('/api/budgets', json={
        'category_id': food_cat['id'],
        'month': 11,
        'year': 2026,
        'amount': 10000
    })
    assert b_res.status_code == 201

    # 2. Spend 8,500 (85% - should trigger 'Warning')
    auth_client.post('/api/expenses', json={
        'category_id': food_cat['id'],
        'amount': 8500,
        'transaction_date': '2026-11-05',
        'description': 'Family Dinner',
        'payment_method': 'Cash'
    })

    budgets_res = auth_client.get('/api/budgets?month=11&year=2026')
    cats = budgets_res.get_json()['data']['categories']
    matched_cat = next(c for c in cats if c['category_id'] == food_cat['id'])
    assert matched_cat['status'] == 'Warning'
    assert matched_cat['percentage'] == 85.0

    # 3. Spend additional 2,000 (total 10,500 - 105% - should trigger 'Exceeded')
    auth_client.post('/api/expenses', json={
        'category_id': food_cat['id'],
        'amount': 2000,
        'transaction_date': '2026-11-06',
        'description': 'Snacks',
        'payment_method': 'Mobile Wallet'
    })

    budgets_res2 = auth_client.get('/api/budgets?month=11&year=2026')
    cats2 = budgets_res2.get_json()['data']['categories']
    matched_cat2 = next(c for c in cats2 if c['category_id'] == food_cat['id'])
    assert matched_cat2['status'] == 'Exceeded'
    assert matched_cat2['percentage'] == 105.0
    assert matched_cat2['remaining'] == -500.0

def test_workflow_4_goal_tracking_and_contribution_lifecycle(auth_client):
    """Workflow 4: Create Goal -> Deposit Contribution -> Progress Recalculation."""
    # 1. Create Goal: target 50,000
    g_res = auth_client.post('/api/goals', json={
        'goal_name': 'Emergency Reserve',
        'target_amount': 50000,
        'starting_amount': 5000,
        'start_date': '2026-01-01',
        'target_date': '2026-12-31',
        'priority': 'High'
    })
    assert g_res.status_code == 201
    goal_id = g_res.get_json()['data']['id']

    # 2. Add Contribution of 20,000
    c_res = auth_client.post(f'/api/goals/{goal_id}/contributions', json={
        'amount': 20000,
        'contribution_date': '2026-11-04',
        'description': 'Bonus allocation'
    })
    assert c_res.status_code == 201

    # 3. Verify Goal progress: (25,000 / 50,000) * 100 = 50%
    goals_res = auth_client.get('/api/goals')
    assert goals_res.status_code == 200
    goals = goals_res.get_json()['data']['goals']
    target_goal = next(g for g in goals if g['id'] == goal_id)
    assert target_goal['current_amount'] == 25000.0
    assert target_goal['progress_percentage'] == 50.0

def test_workflow_5_monthly_analytics_and_period_comparison(auth_client):
    """Workflow 5: Record multi-month data -> Request comparison -> Verify delta calculations."""
    exp_cats = auth_client.get('/api/categories?type=expense').get_json()['data']
    cat_id = exp_cats[0]['id']

    # Month 9: 5,000
    auth_client.post('/api/expenses', json={
        'category_id': cat_id,
        'amount': 5000,
        'transaction_date': '2026-09-10',
        'description': 'Utilities Sep'
    })

    # Month 10: 8,000 (increase of 3,000 = +60%)
    auth_client.post('/api/expenses', json={
        'category_id': cat_id,
        'amount': 8000,
        'transaction_date': '2026-10-12',
        'description': 'Utilities Oct'
    })

    # Request comparison API
    comp_res = auth_client.get('/api/analytics/comparison?m1=9&y1=2026&m2=10&y2=2026')
    assert comp_res.status_code == 200
    comp_data = comp_res.get_json()['data']['categories']

    cat_comp = next(c for c in comp_data if c['category_name'] == exp_cats[0]['name'])
    assert cat_comp['month1_amount'] == 5000.0
    assert cat_comp['month2_amount'] == 8000.0
    assert cat_comp['difference'] == 3000.0
    assert cat_comp['percentage_change'] == 60.0
    assert cat_comp['direction'] == 'increase'
