"""
Analytics Service & Engine (Part C - Rewriting Selected Classes).
Replaces the legacy procedural 350-line god module with an object-oriented AnalyticsEngine.
De-couples SQL data access into the Repository layer and separates domain metric calculations
from presentation formatting (Chart.js payloads).
"""
import datetime
from repositories.transaction_repository import TransactionRepository
from repositories.budget_repository import BudgetRepository
from utils.calculations import (
    calculate_balance,
    calculate_savings,
    calculate_savings_rate,
    calculate_monthly_change
)
from services.budget_service import get_budgets, get_budget_alerts
from services.goal_service import get_goal_alerts

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

class AnalyticsEngine:
    """
    Object-oriented analytics engine computing financial health indicators,
    time-series aggregations, and dashboard metric cards.
    """

    def __init__(self, transaction_repo=None, budget_repo=None):
        self.transaction_repo = transaction_repo or TransactionRepository()
        self.budget_repo = budget_repo or BudgetRepository()

    def get_dashboard_summary(self, user_id, month=None, year=None):
        """Assembles core financial KPIs, chart allocations, and alerts for dashboard."""
        today = datetime.date.today()
        m = int(month) if month else today.month
        y = int(year) if year else today.year

        # 1. Monthly income and expenses via repository
        tot_income = self.transaction_repo.get_total_by_type(user_id, 'income', month=m, year=y)
        tot_expense = self.transaction_repo.get_total_by_type(user_id, 'expense', month=m, year=y)

        # 2. Lifetime balance
        all_income = self.transaction_repo.get_total_by_type(user_id, 'income')
        all_expense = self.transaction_repo.get_total_by_type(user_id, 'expense')
        tot_balance = calculate_balance(all_income, all_expense)

        savings = calculate_savings(tot_income, tot_expense)
        savings_rate = calculate_savings_rate(tot_income, tot_expense)

        # 3. Budget information
        budget_data = get_budgets(user_id, m, y)
        overall_budget = budget_data['overall']['amount']
        budget_remaining = budget_data['overall']['remaining']
        budget_used_pct = budget_data['overall']['percentage']

        # 4. Chart breakdowns
        exp_allocation = self.transaction_repo.get_category_totals(user_id, 'expense', month=m, year=y)
        inc_summary = self.transaction_repo.get_category_totals(user_id, 'income', month=m, year=y)
        recent_txs = self.transaction_repo.get_recent_transactions(user_id, limit=10)

        # 5. Combined alerts
        b_alerts = get_budget_alerts(user_id, m, y)
        g_alerts = get_goal_alerts(user_id)
        combined_alerts = b_alerts + g_alerts

        return {
            'month': m,
            'year': y,
            'metrics': {
                'total_balance': tot_balance,
                'total_income': tot_income,
                'total_expenses': tot_expense,
                'savings': savings,
                'savings_rate': savings_rate,
                'monthly_budget': overall_budget,
                'budget_remaining': budget_remaining,
                'budget_used_percentage': budget_used_pct
            },
            'expense_allocation': exp_allocation,
            'income_summary': inc_summary,
            'budget_categories': budget_data['categories'],
            'recent_transactions': recent_txs,
            'alerts': combined_alerts
        }

    def get_income_analytics(self, user_id, year=None):
        """Assembles annual income statistics, trendline, and top earning sources."""
        y = int(year) if year else datetime.date.today().year

        tot_income = self.transaction_repo.get_total_by_type(user_id, 'income')
        top_source = self.transaction_repo.get_top_category(user_id, 'income', year=y)
        monthly_trend = self.transaction_repo.get_monthly_trend(user_id, 'income', y)

        monthly_dict = {row['month_num']: float(row['total']) for row in monthly_trend}
        trend_data = [monthly_dict.get(i, 0.0) for i in range(1, 13)]

        active_months = [val for val in trend_data if val > 0.0]
        avg_monthly = sum(trend_data) / max(1, len(active_months)) if active_months else 0.0

        return {
            'year': y,
            'total_income': tot_income,
            'avg_monthly_income': round(avg_monthly, 2),
            'top_source': top_source,
            'months': MONTH_NAMES,
            'trend': trend_data
        }

    def get_expense_analytics(self, user_id, year=None):
        """Assembles annual expense statistics, category breakdown, and daily run-rate."""
        y = int(year) if year else datetime.date.today().year

        tot_expense = self.transaction_repo.get_total_by_type(user_id, 'expense')
        top_category = self.transaction_repo.get_top_category(user_id, 'expense', year=y)
        monthly_trend = self.transaction_repo.get_monthly_trend(user_id, 'expense', y)

        monthly_dict = {row['month_num']: float(row['total']) for row in monthly_trend}
        trend_data = [monthly_dict.get(i, 0.0) for i in range(1, 13)]

        days_in_year = 366.0 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365.0
        daily_avg = sum(trend_data) / days_in_year

        cat_breakdown = self.transaction_repo.get_category_totals(user_id, 'expense', year=y)

        return {
            'year': y,
            'total_expense': tot_expense,
            'daily_avg': round(daily_avg, 2),
            'top_category': top_category,
            'months': MONTH_NAMES,
            'trend': trend_data,
            'category_breakdown': cat_breakdown
        }

    def get_detailed_analytics(self, user_id, month=None, year=None):
        """Provides in-depth financial diagnostics for a selected period."""
        today = datetime.date.today()
        m = int(month) if month else today.month
        y = int(year) if year else today.year

        tot_inc = self.transaction_repo.get_total_by_type(user_id, 'income', month=m, year=y)
        tot_exp = self.transaction_repo.get_total_by_type(user_id, 'expense', month=m, year=y)

        sav = calculate_savings(tot_inc, tot_exp)
        sav_rate = calculate_savings_rate(tot_inc, tot_exp)

        cats_exp = self.transaction_repo.get_category_totals(user_id, 'expense', month=m, year=y)
        highest_cat = cats_exp[0]['category_name'] if cats_exp else 'None'
        lowest_cat = cats_exp[-1]['category_name'] if cats_exp else 'None'

        max_tx = self.transaction_repo.get_most_expensive_transaction(user_id, m, y)
        tx_count = self.transaction_repo.get_monthly_transaction_count(user_id, m, y)
        trend_rows = self.transaction_repo.get_cash_flow_trend(user_id, limit=24)

        return {
            'month': m,
            'year': y,
            'metrics': {
                'total_income': tot_inc,
                'total_expenses': tot_exp,
                'savings': sav,
                'savings_rate': sav_rate,
                'highest_spending_category': highest_cat,
                'lowest_spending_category': lowest_cat,
                'most_expensive_transaction': max_tx,
                'transaction_count': tx_count
            },
            'expense_categories': cats_exp,
            'cash_flow_trend': trend_rows
        }

    def get_monthly_comparison(self, user_id, m1, y1, m2, y2):
        """Computes delta and percentage change across categories for any two months."""
        m1_map = self.transaction_repo.get_monthly_category_spending_map(user_id, m1, y1)
        m2_map = self.transaction_repo.get_monthly_category_spending_map(user_id, m2, y2)

        all_cats = sorted(list(set(m1_map.keys()).union(set(m2_map.keys()))))
        comparison = []

        for cat in all_cats:
            v1 = m1_map.get(cat, 0.0)
            v2 = m2_map.get(cat, 0.0)
            diff = v2 - v1
            pct_change = calculate_monthly_change(v2, v1)
            direction = 'increase' if diff > 0 else ('decrease' if diff < 0 else 'unchanged')

            comparison.append({
                'category_name': cat,
                'month1_amount': v1,
                'month2_amount': v2,
                'difference': diff,
                'percentage_change': pct_change,
                'direction': direction
            })

        return {
            'month1': {'month': m1, 'year': y1},
            'month2': {'month': m2, 'year': y2},
            'categories': comparison
        }

# Module-level singleton instance & backward-compatible function proxies
_default_analytics_engine = AnalyticsEngine()

def get_dashboard_summary(*args, **kwargs):
    return _default_analytics_engine.get_dashboard_summary(*args, **kwargs)

def get_income_analytics(*args, **kwargs):
    return _default_analytics_engine.get_income_analytics(*args, **kwargs)

def get_expense_analytics(*args, **kwargs):
    return _default_analytics_engine.get_expense_analytics(*args, **kwargs)

def get_detailed_analytics(*args, **kwargs):
    return _default_analytics_engine.get_detailed_analytics(*args, **kwargs)

def get_monthly_comparison(*args, **kwargs):
    return _default_analytics_engine.get_monthly_comparison(*args, **kwargs)
