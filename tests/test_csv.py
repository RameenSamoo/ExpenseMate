import pytest

def test_csv_export_and_import(auth_client):
    # 1. Test CSV Import
    csv_payload = "Date,Type,Category,Amount,Description\n2026-09-01,income,Salary,100000,Monthly Pay\n2026-09-02,expense,Food,5000,Groceries\ninvalid-date,expense,Food,100,Bad Row\n"
    res = auth_client.post('/api/import', data=csv_payload, content_type='text/csv')
    assert res.status_code == 200
    summary = res.get_json()['summary']
    assert summary['imported'] == 2
    assert summary['rejected'] == 1

    # 2. Test CSV Export
    exp_res = auth_client.get('/api/export')
    assert exp_res.status_code == 200
    csv_text = exp_res.get_data(as_text=True)
    assert 'Date,Type,Category,Amount,Description' in csv_text
    assert 'Salary' in csv_text
    assert 'Groceries' in csv_text
