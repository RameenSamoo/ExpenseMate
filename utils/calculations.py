"""
Calculations Module (Facade / Backward-Compatibility Layer).
Delegates all operations to the rewritten object-oriented engines:
- FinancialCalculator
- BudgetAnalyzer
- GoalTracker
"""
from engines.financial_calculator import (
    FinancialCalculator,
    BudgetAnalyzer,
    GoalTracker
)

# Shared default budget analyzer instance
_default_analyzer = BudgetAnalyzer()

def calculate_balance(total_income, total_expenses):
    return FinancialCalculator.calculate_balance(total_income, total_expenses)

def calculate_savings(total_income, total_expenses):
    return FinancialCalculator.calculate_savings(total_income, total_expenses)

def calculate_savings_rate(total_income, total_expenses):
    return FinancialCalculator.calculate_savings_rate(total_income, total_expenses)

def calculate_budget_remaining(budget_amount, spent_amount):
    return _default_analyzer.calculate_remaining(budget_amount, spent_amount)

def calculate_budget_percentage(budget_amount, spent_amount):
    return _default_analyzer.calculate_percentage(budget_amount, spent_amount)

def determine_budget_status(percentage):
    return _default_analyzer.determine_status(percentage)

def calculate_goal_progress(current_amount, target_amount):
    return GoalTracker.calculate_progress(current_amount, target_amount)

def calculate_goal_remaining(target_amount, current_amount):
    return GoalTracker.calculate_remaining(target_amount, current_amount)

def parse_date(date_val):
    return GoalTracker.parse_date(date_val)

def calculate_required_monthly_contribution(target_amount, current_amount, target_date_str, ref_date=None):
    return GoalTracker.calculate_required_monthly_contribution(target_amount, current_amount, target_date_str, ref_date)

def calculate_expected_goal_progress(start_date_str, target_date_str, ref_date=None):
    return GoalTracker.calculate_expected_progress(start_date_str, target_date_str, ref_date)

def determine_goal_status(current_amount, target_amount, start_date_str, target_date_str, ref_date=None):
    return GoalTracker.determine_status(current_amount, target_amount, start_date_str, target_date_str, ref_date)

def calculate_monthly_change(current_val, previous_val):
    return FinancialCalculator.calculate_monthly_change(current_val, previous_val)
