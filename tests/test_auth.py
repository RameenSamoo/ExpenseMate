import pytest

def test_register_user(client):
    res = client.post('/api/auth/register', json={
        'full_name': 'Test User',
        'email': 'test@expensemate.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    data = res.get_json()
    assert res.status_code == 201
    assert data['success'] is True
    assert data['user']['email'] == 'test@expensemate.com'

def test_duplicate_email_registration(client):
    client.post('/api/auth/register', json={
        'full_name': 'Test User',
        'email': 'dup@expensemate.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    res = client.post('/api/auth/register', json={
        'full_name': 'Another User',
        'email': 'dup@expensemate.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    data = res.get_json()
    assert res.status_code == 400
    assert data['success'] is False

def test_login_user(client):
    client.post('/api/auth/register', json={
        'full_name': 'Login User',
        'email': 'login@expensemate.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    res = client.post('/api/auth/login', json={
        'email': 'login@expensemate.com',
        'password': 'password123'
    })
    data = res.get_json()
    assert res.status_code == 200
    assert data['success'] is True
