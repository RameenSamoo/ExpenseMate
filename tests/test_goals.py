import pytest

def test_goals_and_contributions(auth_client):
    # 1. Create Goal
    res = auth_client.post('/api/goals', json={
        'goal_name': 'New Phone',
        'start_date': '2026-01-01',
        'target_date': '2026-12-31',
        'target_amount': 100000,
        'starting_amount': 10000,
        'priority': 'High'
    })
    assert res.status_code == 201
    goal_id = res.get_json()['data']['id']
    assert res.get_json()['data']['progress_percentage'] == 10.0

    # 2. Add Contribution of 40,000 -> Current Saved = 50,000 (50%)
    res = auth_client.post(f'/api/goals/{goal_id}/contributions', json={
        'amount': 40000,
        'contribution_date': '2026-09-01',
        'description': 'Bonus deposit'
    })
    assert res.status_code == 201
    goal_data = res.get_json()['data']
    assert goal_data['current_amount'] == 50000.0
    assert goal_data['progress_percentage'] == 50.0

    # 3. Add final contribution of 50,000 -> 100% Completed
    res = auth_client.post(f'/api/goals/{goal_id}/contributions', json={
        'amount': 50000,
        'contribution_date': '2026-09-02'
    })
    assert res.get_json()['data']['status'] == 'Completed'
