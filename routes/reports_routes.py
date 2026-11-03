from flask import Blueprint, request, jsonify, render_template, session
from services.analytics_service import get_dashboard_summary, get_expense_analytics
from services.goal_service import get_goals
from utils.decorators import login_required
import datetime

reports_bp = Blueprint('reports_routes', __name__)

@reports_bp.route('/reports', methods=['GET'])
@login_required
def reports_view():
    return render_template('reports.html', user_name=session.get('full_name', 'User'))

@reports_bp.route('/api/reports', methods=['GET'])
@login_required
def api_get_report():
    user_id = session['user_id']
    today = datetime.date.today()
    month = request.args.get('month', today.month)
    year = request.args.get('year', today.year)

    summary = get_dashboard_summary(user_id, month=month, year=year)
    exp_analytics = get_expense_analytics(user_id, year=year)
    goals_data = get_goals(user_id)

    report_data = {
        'month': int(month),
        'year': int(year),
        'generated_at': today.strftime('%Y-%m-%d'),
        'user_name': session.get('full_name'),
        'metrics': summary['metrics'],
        'top_spending_category': exp_analytics['top_category'],
        'expense_allocation': summary['expense_allocation'],
        'income_summary': summary['income_summary'],
        'budget_categories': summary['budget_categories'],
        'goals_summary': goals_data['summary'],
        'goals_list': goals_data['goals']
    }

    return jsonify({'success': True, 'data': report_data})
