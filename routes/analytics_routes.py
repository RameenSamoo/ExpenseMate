from flask import Blueprint, request, jsonify, render_template, session
from services.analytics_service import (
    get_detailed_analytics,
    get_income_analytics,
    get_expense_analytics,
    get_monthly_comparison
)
from utils.decorators import login_required
import datetime

analytics_bp = Blueprint('analytics_routes', __name__)

@analytics_bp.route('/analytics', methods=['GET'])
@login_required
def analytics_view():
    return render_template('analytics.html', user_name=session.get('full_name', 'User'))

@analytics_bp.route('/api/analytics', methods=['GET'])
@login_required
def api_get_analytics():
    user_id = session['user_id']
    today = datetime.date.today()
    month = request.args.get('month', today.month)
    year = request.args.get('year', today.year)

    data = get_detailed_analytics(user_id, month=month, year=year)
    return jsonify({'success': True, 'data': data})

@analytics_bp.route('/api/analytics/monthly', methods=['GET'])
@login_required
def api_get_monthly_analytics():
    user_id = session['user_id']
    year = request.args.get('year')
    inc_data = get_income_analytics(user_id, year=year)
    exp_data = get_expense_analytics(user_id, year=year)

    return jsonify({
        'success': True,
        'data': {
            'income': inc_data,
            'expenses': exp_data
        }
    })

@analytics_bp.route('/api/analytics/category', methods=['GET'])
@login_required
def api_get_category_analytics():
    user_id = session['user_id']
    year = request.args.get('year')
    exp_data = get_expense_analytics(user_id, year=year)
    return jsonify({'success': True, 'data': exp_data['category_breakdown']})

@analytics_bp.route('/api/analytics/comparison', methods=['GET'])
@login_required
def api_get_monthly_comparison():
    user_id = session['user_id']
    today = datetime.date.today()
    m1 = int(request.args.get('m1', today.month - 1 if today.month > 1 else 12))
    y1 = int(request.args.get('y1', today.year if today.month > 1 else today.year - 1))
    m2 = int(request.args.get('m2', today.month))
    y2 = int(request.args.get('y2', today.year))

    data = get_monthly_comparison(user_id, m1, y1, m2, y2)
    return jsonify({'success': True, 'data': data})
