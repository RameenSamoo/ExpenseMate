"""
Financial Calculation & Domain Analysis Engine (Part C - Rewriting Selected Classes).
Replaces legacy procedural calculations with encapsulated, object-oriented domain engines:
1. FinancialCalculator: Core monetary math, safe division, rounding, and net balance/savings calculations.
2. BudgetAnalyzer: Threshold policy management, utilization metrics, and status evaluation.
3. GoalTracker: Timeline velocity, target forecasting, contribution scheduling, and deadline tracking.
"""
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP

class FinancialCalculator:
    """Core mathematical and financial metrics calculator with high precision."""

    @staticmethod
    def to_float(val, default=0.0):
        """Safely parses any numeric or null value to float."""
        if val is None:
            return float(default)
        try:
            return float(val)
        except (ValueError, TypeError):
            return float(default)

    @classmethod
    def calculate_balance(cls, total_income, total_expenses):
        """Net Balance = Total Income - Total Expenses."""
        inc = cls.to_float(total_income)
        exp = cls.to_float(total_expenses)
        return round(inc - exp, 2)

    @classmethod
    def calculate_savings(cls, total_income, total_expenses):
        """Savings = Total Income - Total Expenses."""
        return cls.calculate_balance(total_income, total_expenses)

    @classmethod
    def calculate_savings_rate(cls, total_income, total_expenses):
        """Savings Rate percentage = (Savings / Income) * 100."""
        inc = cls.to_float(total_income)
        exp = cls.to_float(total_expenses)
        if inc <= 0:
            return 0.0
        savings = inc - exp
        rate = (savings / inc) * 100.0
        return round(rate, 1)

    @classmethod
    def calculate_monthly_change(cls, current_val, previous_val):
        """Calculates percentage change between two monthly metrics."""
        curr = cls.to_float(current_val)
        prev = cls.to_float(previous_val)
        if prev == 0.0:
            return 100.0 if curr > 0.0 else 0.0
        change = ((curr - prev) / abs(prev)) * 100.0
        return round(change, 1)


class BudgetAnalyzer:
    """
    Object-oriented budget analyzer that evaluates spending against defined thresholds.
    Eliminates hardcoded magic numbers by allowing configurable warning and exceeded limits.
    """

    DEFAULT_WARNING_THRESHOLD = 80.0
    DEFAULT_EXCEEDED_THRESHOLD = 100.0

    def __init__(self, warning_threshold=DEFAULT_WARNING_THRESHOLD, exceeded_threshold=DEFAULT_EXCEEDED_THRESHOLD):
        self.warning_threshold = float(warning_threshold)
        self.exceeded_threshold = float(exceeded_threshold)

    def calculate_remaining(self, budget_amount, spent_amount):
        """Remaining Budget = Budget Amount - Spent Amount."""
        b = FinancialCalculator.to_float(budget_amount)
        s = FinancialCalculator.to_float(spent_amount)
        return round(b - s, 2)

    def calculate_percentage(self, budget_amount, spent_amount):
        """Percentage utilized = (Spent / Budget) * 100."""
        b = FinancialCalculator.to_float(budget_amount)
        s = FinancialCalculator.to_float(spent_amount)
        if b <= 0.0:
            return 0.0
        pct = (s / b) * 100.0
        return round(pct, 1)

    def determine_status(self, percentage):
        """
        Evaluates budget health based on configurable threshold boundaries:
        - percentage >= exceeded_threshold -> 'Exceeded'
        - percentage >= warning_threshold  -> 'Warning'
        - otherwise                        -> 'Normal'
        """
        p = FinancialCalculator.to_float(percentage)
        if p >= self.exceeded_threshold:
            return 'Exceeded'
        elif p >= self.warning_threshold:
            return 'Warning'
        return 'Normal'

    def analyze(self, budget_amount, spent_amount):
        """Returns a comprehensive evaluation dictionary for a given budget & spent pair."""
        b = FinancialCalculator.to_float(budget_amount)
        s = FinancialCalculator.to_float(spent_amount)
        pct = self.calculate_percentage(b, s)
        rem = self.calculate_remaining(b, s)
        status = self.determine_status(pct)
        return {
            'budget': b,
            'spent': s,
            'remaining': rem,
            'percentage': pct,
            'status': status
        }


class GoalTracker:
    """
    Domain class managing savings goal timelines, contribution requirements,
    and velocity tracking.
    """

    @staticmethod
    def parse_date(date_val):
        """Converts strings, dates, or datetimes to a unified date object."""
        if isinstance(date_val, date) and not isinstance(date_val, datetime):
            return date_val
        if isinstance(date_val, datetime):
            return date_val.date()
        return datetime.strptime(str(date_val)[:10], '%Y-%m-%d').date()

    @classmethod
    def calculate_progress(cls, current_amount, target_amount):
        """Goal completion percentage = (Current Saved / Target) * 100 (capped at 100)."""
        target = FinancialCalculator.to_float(target_amount)
        current = FinancialCalculator.to_float(current_amount)
        if target <= 0.0:
            return 0.0
        progress = (current / target) * 100.0
        return min(round(progress, 1), 100.0)

    @classmethod
    def calculate_remaining(cls, target_amount, current_amount):
        """Remaining amount required to hit goal target."""
        target = FinancialCalculator.to_float(target_amount)
        current = FinancialCalculator.to_float(current_amount)
        rem = target - current
        return max(0.0, round(rem, 2))

    @classmethod
    def calculate_required_monthly_contribution(cls, target_amount, current_amount, target_date_str, ref_date=None):
        """Calculates necessary monthly contribution to complete the goal on schedule."""
        target = FinancialCalculator.to_float(target_amount)
        current = FinancialCalculator.to_float(current_amount)
        rem_amt = target - current
        if rem_amt <= 0.0:
            return 0.0

        today = cls.parse_date(ref_date or date.today())
        target_dt = cls.parse_date(target_date_str)

        months_left = (target_dt.year - today.year) * 12 + (target_dt.month - today.month)
        if months_left <= 0:
            return round(rem_amt, 2)

        return round(rem_amt / months_left, 2)

    @classmethod
    def calculate_expected_progress(cls, start_date_str, target_date_str, ref_date=None):
        """Calculates expected progress based on time elapsed since start date."""
        start_dt = cls.parse_date(start_date_str)
        target_dt = cls.parse_date(target_date_str)
        today = cls.parse_date(ref_date or date.today())

        total_days = (target_dt - start_dt).days
        if total_days <= 0:
            return 100.0

        elapsed_days = (today - start_dt).days
        if elapsed_days <= 0:
            return 0.0

        expected = (elapsed_days / total_days) * 100.0
        return min(round(expected, 1), 100.0)

    @classmethod
    def determine_status(cls, current_amount, target_amount, start_date_str, target_date_str, ref_date=None):
        """
        Determines goal status based on timeline velocity and target completion.
        Statuses: 'Completed', 'Deadline Approaching', 'Behind Schedule', 'On Track', 'In Progress', 'Not Started'.
        """
        target = FinancialCalculator.to_float(target_amount)
        current = FinancialCalculator.to_float(current_amount)
        if current >= target and target > 0.0:
            return 'Completed'

        today = cls.parse_date(ref_date or date.today())
        start_dt = cls.parse_date(start_date_str)
        target_dt = cls.parse_date(target_date_str)

        if today < start_dt and current == 0.0:
            return 'Not Started'

        days_to_deadline = (target_dt - today).days
        actual_progress = cls.calculate_progress(current, target)
        expected_progress = cls.calculate_expected_progress(start_date_str, target_date_str, today)

        if 0 <= days_to_deadline <= 30 and actual_progress < 100.0:
            return 'Deadline Approaching'
        if actual_progress < (expected_progress - 10.0):
            return 'Behind Schedule'
        if actual_progress >= expected_progress:
            return 'On Track'

        return 'In Progress'
