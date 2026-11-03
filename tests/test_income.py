import pytest

def test_income_crud(auth_client):
    cats = auth_client.get('/api/categories?type=income').get_json()['data']
    cat_id = cats[0]['id']

    # 1. Add Income
    res = auth_client.post('/api/income', json={
        'category_id': cat_id,
        'amount': 50000,
        'transaction_date': '2026-09-01',
        'description': 'Monthly Paycheck'
    })
    assert res.status_code == 201
    inc_id = res.get_json()['data']['id']

    # 2. Get Income
    res = auth_client.get('/api/income')
    assert res.status_code == 200
    assert len(res.get_json()['data']['items']) == 1

    # 3. Update Income
    res = auth_client.put(f'/api/income/{inc_id}', json={
        'amount': 55000,
        'description': 'Updated Paycheck'
    })
    assert res.status_code == 200
    assert res.get_json()['data']['amount'] == 55000.0

    # 4. Delete Income
    res = auth_client.delete(f'/api/income/{inc_id}')
    assert res.status_code == 200

    # 5. Verify empty
    res = auth_client.get('/api/income')
    assert len(res.get_json()['data']['items']) == 0
