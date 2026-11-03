import pytest

def test_analytics_calculations(auth_client):
    inc_cats = auth_client.get('/api/categories?type=income').get_json()['data']
    exp_cats = auth_client.get('/api/categories?type=expense').get_json()['data']

    # Income 100,000
    auth_client.post('/api/income', json={
        'category_id': inc_cats[0]['id'],
        'amount': 100000,
        'transaction_date': '2026-09-01'
    })
    # Expense 30,000
    auth_client.post('/api/expenses', json={
        'category_id': exp_cats[0]['id'],
        'amount': 30000,
        'transaction_date': '2026-09-02'
    })

    res = auth_client.get('/api/analytics?month=9&year=2026')
    m = res.get_json()['data']['metrics']

    assert m['total_income'] == 100000.0
    assert m['total_expenses'] == 30000.0
    assert m['savings'] == 70000.0
    assert m['savings_rate'] == 70.0
