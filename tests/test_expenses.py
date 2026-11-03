import pytest

def test_expense_crud(auth_client):
    cats = auth_client.get('/api/categories?type=expense').get_json()['data']
    cat_id = cats[0]['id']

    # 1. Add Expense
    res = auth_client.post('/api/expenses', json={
        'category_id': cat_id,
        'amount': 1500,
        'transaction_date': '2026-09-02',
        'description': 'Supermarket Groceries'
    })
    assert res.status_code == 201
    exp_id = res.get_json()['data']['id']

    # 2. Get Expenses
    res = auth_client.get('/api/expenses')
    assert res.status_code == 200
    assert len(res.get_json()['data']['items']) == 1

    # 3. Delete Expense
    res = auth_client.delete(f'/api/expenses/{exp_id}')
    assert res.status_code == 200
    assert res.get_json()['success'] is True
