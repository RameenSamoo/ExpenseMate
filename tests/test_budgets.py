import pytest

def test_budget_creation_and_alerts(auth_client):
    cats = auth_client.get('/api/categories?type=expense').get_json()['data']
    cat_id = cats[0]['id']

    # Set category budget limit to 10,000 for Sep 2026
    res = auth_client.post('/api/budgets', json={
        'month': 9,
        'year': 2026,
        'amount': 10000,
        'category_id': cat_id
    })
    assert res.status_code == 201

    # Add expense of 8,500 (85% -> Warning)
    auth_client.post('/api/expenses', json={
        'category_id': cat_id,
        'amount': 8500,
        'transaction_date': '2026-09-05',
        'description': 'Test spend'
    })

    res = auth_client.get('/api/budgets?month=9&year=2026')
    b_data = res.get_json()['data']
    cat_b = b_data['categories'][0]
    assert cat_b['amount'] == 10000.0
    assert cat_b['spent'] == 8500.0
    assert cat_b['status'] == 'Warning'

def test_yearly_budget_analytics(auth_client):
    res = auth_client.get('/api/budgets/yearly?year=2026')
    assert res.status_code == 200
    data = res.get_json()['data']
    assert 'overall' in data
    assert 'months' in data
    assert 'budget_trend' in data
    assert 'spent_trend' in data
    assert len(data['months']) == 12

