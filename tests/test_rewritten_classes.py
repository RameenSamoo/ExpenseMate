"""
Unit Tests for Rewritten Classes (Part C - Rewriting Selected Classes).
Tests the isolated logic of:
1. FinancialCalculator
2. BudgetAnalyzer
3. GoalTracker
4. AnalyticsEngine
"""
import pytest
from engines.financial_calculator import FinancialCalculator, BudgetAnalyzer, GoalTracker
from services.analytics_service import AnalyticsEngine
from datetime import date, timedelta

def test_financial_calculator_core_math():
    # Balance & Savings
    assert FinancialCalculator.calculate_balance(10000.50, 4500.25) == 5500.25
    assert FinancialCalculator.calculate_balance(None, 200.0) == -200.0

    # Savings Rate
    assert FinancialCalculator.calculate_savings_rate(10000, 3000) == 70.0
    assert FinancialCalculator.calculate_savings_rate(0, 500) == 0.0  # Division by zero safety
    assert FinancialCalculator.calculate_savings_rate(-100, 50) == 0.0

    # Monthly Change
    assert FinancialCalculator.calculate_monthly_change(1500, 1000) == 50.0
    assert FinancialCalculator.calculate_monthly_change(500, 1000) == -50.0
    assert FinancialCalculator.calculate_monthly_change(500, 0) == 100.0
    assert FinancialCalculator.calculate_monthly_change(0, 0) == 0.0

def test_budget_analyzer_thresholds_and_status():
    analyzer = BudgetAnalyzer(warning_threshold=75.0, exceeded_threshold=100.0)

    # Under warning threshold
    res1 = analyzer.analyze(10000.0, 5000.0)
    assert res1['percentage'] == 50.0
    assert res1['remaining'] == 5000.0
    assert res1['status'] == 'Normal'

    # Warning range (75% - 99.9%)
    res2 = analyzer.analyze(10000.0, 8000.0)
    assert res2['percentage'] == 80.0
    assert res2['status'] == 'Warning'

    # Exceeded range (>= 100%)
    res3 = analyzer.analyze(10000.0, 12000.0)
    assert res3['percentage'] == 120.0
    assert res3['remaining'] == -2000.0
    assert res3['status'] == 'Exceeded'

    # Zero budget protection
    res_zero = analyzer.analyze(0.0, 500.0)
    assert res_zero['percentage'] == 0.0

def test_goal_tracker_velocity_and_deadlines():
    today = date(2026, 11, 1)

    # 1. Progress
    assert GoalTracker.calculate_progress(5000, 10000) == 50.0
    assert GoalTracker.calculate_progress(15000, 10000) == 100.0 # Capped at 100%
    assert GoalTracker.calculate_progress(500, 0) == 0.0

    # 2. Required Monthly Contribution
    # 5 months left (Nov 2026 to Apr 2027), remaining 5000 -> 1000/month
    req = GoalTracker.calculate_required_monthly_contribution(
        target_amount=10000,
        current_amount=5000,
        target_date_str='2027-04-01',
        ref_date=today
    )
    assert req == 1000.0

    # 3. Status - Deadline approaching (within 30 days)
    near_target = '2026-11-20'
    status_near = GoalTracker.determine_status(
        current_amount=2000,
        target_amount=10000,
        start_date_str='2026-06-01',
        target_date_str=near_target,
        ref_date=today
    )
    assert status_near == 'Deadline Approaching'

    # 4. Status - Completed
    status_done = GoalTracker.determine_status(
        current_amount=10000,
        target_amount=10000,
        start_date_str='2026-01-01',
        target_date_str='2026-12-31',
        ref_date=today
    )
    assert status_done == 'Completed'

def test_analytics_engine_dashboard_aggregation(app, auth_client):
    """Verifies AnalyticsEngine functions correctly within the layered system."""
    with app.app_context():
        engine = AnalyticsEngine()
        user_id = 1
        summary = engine.get_dashboard_summary(user_id=user_id, month=11, year=2026)

        assert 'metrics' in summary
        assert 'total_balance' in summary['metrics']
        assert 'expense_allocation' in summary
        assert 'alerts' in summary
