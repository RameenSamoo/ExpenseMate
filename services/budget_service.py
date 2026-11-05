"""
Budget Service (Layered Architecture - Part B).
Contains application & business logic, budget calculations, status evaluation, and alert generation.
Delegates all database access exclusively to BudgetRepository, TransactionRepository, and CategoryRepository.
No SQL is executed directly in this service layer.
"""
import datetime
from repositories.budget_repository import BudgetRepository
from repositories.transaction_repository import TransactionRepository
from repositories.category_repository import CategoryRepository
from utils.calculations import (
    calculate_budget_remaining,
    calculate_budget_percentage,
    determine_budget_status
)
from utils.validators import is_non_negative_number

class BudgetService:
    def __init__(self, budget_repo=None, transaction_repo=None, category_repo=None):
        self.budget_repo = budget_repo or BudgetRepository()
        self.transaction_repo = transaction_repo or TransactionRepository()
        self.category_repo = category_repo or CategoryRepository()

    def set_budget(self, user_id, month, year, amount, category_id=None):
        """Validates input, checks category constraints, and saves budget through repository."""
        try:
            month = int(month)
            year = int(year)
        except (ValueError, TypeError):
            return False, "Invalid month or year."

        if month < 1 or month > 12:
            return False, "Month must be between 1 and 12."
        if year < 2000:
            return False, "Year must be 2000 or later."
        if not is_non_negative_number(amount):
            return False, "Budget amount must be zero or positive."

        if category_id:
            category = self.category_repo.get_by_id(user_id, category_id)
            if not category or category['type'] != 'expense':
                return False, "Invalid expense category selected for budget."

            budget_id = self.budget_repo.upsert_category_budget(
                user_id=user_id,
                category_id=category_id,
                month=month,
                year=year,
                amount=float(amount)
            )
        else:
            budget_id = self.budget_repo.upsert_overall_budget(
                user_id=user_id,
                month=month,
                year=year,
                amount=float(amount)
            )

        return True, self.budget_repo.get_by_id(user_id, budget_id)

    def get_budget_by_id(self, user_id, budget_id):
        return self.budget_repo.get_by_id(user_id, budget_id)

    def delete_budget(self, user_id, budget_id):
        b = self.budget_repo.get_by_id(user_id, budget_id)
        if not b:
            return False, "Budget not found or access denied."
        self.budget_repo.delete(user_id, budget_id)
        return True, "Budget deleted successfully."

    def get_monthly_budget_summary(self, user_id, month, year):
        """
        Coordinates Feature 2: Monthly Budget Summary.
        Fetches raw budget and spending data from repositories and performs business computations:
        - Remaining amount
        - Percentage utilized
        - Budget status threshold (Normal, Warning, Exceeded)
        """
        # 1. Fetch raw overall budget from repository
        overall = self.budget_repo.get_overall_budget(user_id, month, year)
        overall_amount = float(overall['amount']) if overall else 0.0

        # 2. Fetch total monthly spent from transaction repository
        overall_spent = self.transaction_repo.get_monthly_spending(user_id, month, year)

        # 3. Fetch category-specific budgets from repository
        cat_budgets = self.budget_repo.get_category_budgets(user_id, month, year)

        processed_categories = []
        for item in cat_budgets:
            b_amt = float(item['amount'])
            # Fetch category spending from transaction repository
            s_amt = self.transaction_repo.get_category_monthly_spending(user_id, item['category_id'], month, year)
            pct = calculate_budget_percentage(b_amt, s_amt)
            rem = calculate_budget_remaining(b_amt, s_amt)
            status = determine_budget_status(pct)
            processed_categories.append({
                'id': item['id'],
                'category_id': item['category_id'],
                'category_name': item['category_name'],
                'amount': b_amt,
                'spent': s_amt,
                'remaining': rem,
                'percentage': pct,
                'status': status
            })

        # Calculate overall metrics
        overall_pct = calculate_budget_percentage(overall_amount, overall_spent)
        overall_rem = calculate_budget_remaining(overall_amount, overall_spent)
        overall_status = determine_budget_status(overall_pct)

        return {
            'month': month,
            'year': year,
            'overall': {
                'id': overall['id'] if overall else None,
                'amount': overall_amount,
                'spent': overall_spent,
                'remaining': overall_rem,
                'percentage': overall_pct,
                'status': overall_status
            },
            'categories': processed_categories
        }

    def get_budgets(self, user_id, month, year):
        """Alias for get_monthly_budget_summary preserving legacy interface."""
        return self.get_monthly_budget_summary(user_id, month, year)

    def get_budget_alerts(self, user_id, month, year):
        data = self.get_monthly_budget_summary(user_id, month, year)
        alerts = []

        ov = data['overall']
        if ov['amount'] > 0:
            if ov['status'] == 'Exceeded':
                alerts.append({
                    'type': 'danger',
                    'title': 'Overall Budget Exceeded',
                    'message': f"Your total monthly budget has been exceeded! You spent Rs. {ov['spent']:,.2f} of Rs. {ov['amount']:,.2f}."
                })
            elif ov['status'] == 'Warning':
                alerts.append({
                    'type': 'warning',
                    'title': 'Overall Budget Warning',
                    'message': f"Your total monthly budget is {ov['percentage']}% used. Only Rs. {ov['remaining']:,.2f} remains."
                })

        for cat in data['categories']:
            if cat['status'] == 'Exceeded':
                alerts.append({
                    'type': 'danger',
                    'title': f"{cat['category_name']} Budget Exceeded",
                    'message': f"{cat['category_name']} budget has been exceeded ({cat['percentage']}% used). Spent Rs. {cat['spent']:,.2f} of Rs. {cat['amount']:,.2f}."
                })
            elif cat['status'] == 'Warning':
                alerts.append({
                    'type': 'warning',
                    'title': f"{cat['category_name']} Budget Warning",
                    'message': f"{cat['category_name']} budget is {cat['percentage']}% used. Only Rs. {cat['remaining']:,.2f} remains."
                })

        return alerts

    def get_yearly_budget_analytics(self, user_id, year):
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = datetime.date.today().year

        overall_budgets = self.budget_repo.get_annual_overall_budgets(user_id, year)
        month_overall_map = {row['month']: float(row['amount']) for row in overall_budgets}
        annual_overall_budget = sum(month_overall_map.values())

        monthly_expenses = self.transaction_repo.get_annual_monthly_expenses(user_id, year)
        month_spent_map = {row['month_num']: float(row['total']) for row in monthly_expenses}
        annual_total_spent = sum(month_spent_map.values())

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly_breakdown = []
        budget_trend = []
        spent_trend = []

        for m in range(1, 13):
            b_amt = month_overall_map.get(m, 0.0)
            s_amt = month_spent_map.get(m, 0.0)
            pct = calculate_budget_percentage(b_amt, s_amt)
            monthly_breakdown.append({
                'month': m,
                'month_name': month_names[m-1],
                'budget': b_amt,
                'spent': s_amt,
                'percentage': pct,
                'remaining': calculate_budget_remaining(b_amt, s_amt)
            })
            budget_trend.append(b_amt)
            spent_trend.append(s_amt)

        cat_budgets = self.budget_repo.get_annual_category_budgets(user_id, year)
        processed_categories = []
        for item in cat_budgets:
            b_amt = float(item['annual_budget'])
            s_amt = float(item['annual_spent'])
            pct = calculate_budget_percentage(b_amt, s_amt)
            rem = calculate_budget_remaining(b_amt, s_amt)
            status = determine_budget_status(pct)
            processed_categories.append({
                'category_id': item['category_id'],
                'category_name': item['category_name'],
                'annual_budget': b_amt,
                'annual_spent': s_amt,
                'remaining': rem,
                'percentage': pct,
                'status': status
            })

        annual_pct = calculate_budget_percentage(annual_overall_budget, annual_total_spent)
        annual_rem = calculate_budget_remaining(annual_overall_budget, annual_total_spent)
        annual_status = determine_budget_status(annual_pct)

        return {
            'year': year,
            'overall': {
                'annual_budget': annual_overall_budget,
                'annual_spent': annual_total_spent,
                'annual_remaining': annual_rem,
                'percentage': annual_pct,
                'status': annual_status
            },
            'months': month_names,
            'budget_trend': budget_trend,
            'spent_trend': spent_trend,
            'monthly_breakdown': monthly_breakdown,
            'categories': processed_categories
        }

# Module-level singleton instance & backward-compatible function proxies
_default_budget_service = BudgetService()

def set_budget(*args, **kwargs):
    return _default_budget_service.set_budget(*args, **kwargs)

def get_budget_by_id(*args, **kwargs):
    return _default_budget_service.get_budget_by_id(*args, **kwargs)

def delete_budget(*args, **kwargs):
    return _default_budget_service.delete_budget(*args, **kwargs)

def get_budgets(*args, **kwargs):
    return _default_budget_service.get_budgets(*args, **kwargs)

def get_budget_alerts(*args, **kwargs):
    return _default_budget_service.get_budget_alerts(*args, **kwargs)

def get_yearly_budget_analytics(*args, **kwargs):
    return _default_budget_service.get_yearly_budget_analytics(*args, **kwargs)
