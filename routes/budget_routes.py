from flask import Blueprint, request, jsonify, render_template, session
from services.budget_service import set_budget, get_budgets, delete_budget, get_yearly_budget_analytics
from utils.decorators import login_required
import datetime

budget_bp = Blueprint('budget_routes', __name__)

@budget_bp.route('/budgets', methods=['GET'])
@login_required
def budgets_view():
    return render_template('budgets.html', user_name=session.get('full_name', 'User'))

@budget_bp.route('/api/budgets', methods=['GET'])
@login_required
def api_get_budgets():
    user_id = session['user_id']
    today = datetime.date.today()
    month = request.args.get('month', today.month)
    year = request.args.get('year', today.year)

    result = get_budgets(user_id, month=int(month), year=int(year))
    return jsonify({'success': True, 'data': result})

@budget_bp.route('/api/budgets/yearly', methods=['GET'])
@login_required
def api_get_yearly_budgets():
    user_id = session['user_id']
    today = datetime.date.today()
    year = request.args.get('year', today.year)

    result = get_yearly_budget_analytics(user_id, year=int(year))
    return jsonify({'success': True, 'data': result})

@budget_bp.route('/api/budgets', methods=['POST'])
@login_required
def api_set_budget():
    user_id = session['user_id']
    data = request.get_json() or {}
    success, result = set_budget(
        user_id=user_id,
        month=data.get('month'),
        year=data.get('year'),
        amount=data.get('amount'),
        category_id=data.get('category_id')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Budget saved successfully.', 'data': result}), 201

@budget_bp.route('/api/budgets/<int:budget_id>', methods=['PUT'])
@login_required
def api_update_budget(budget_id):
    user_id = session['user_id']
    data = request.get_json() or {}
    success, result = set_budget(
        user_id=user_id,
        month=data.get('month'),
        year=data.get('year'),
        amount=data.get('amount'),
        category_id=data.get('category_id')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Budget updated successfully.', 'data': result})

@budget_bp.route('/api/budgets/<int:budget_id>', methods=['DELETE'])
@login_required
def api_delete_budget(budget_id):
    user_id = session['user_id']
    success, result = delete_budget(user_id, budget_id)
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': result})
