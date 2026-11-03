from flask import Blueprint, request, jsonify, session
from services.recurring_service import get_recurring_expenses, add_recurring_expense, delete_recurring_expense
from utils.decorators import login_required

recurring_bp = Blueprint('recurring_routes', __name__)

@recurring_bp.route('/api/recurring', methods=['GET'])
@login_required
def api_get_recurring():
    user_id = session['user_id']
    data = get_recurring_expenses(user_id)
    return jsonify({'success': True, 'data': data})

@recurring_bp.route('/api/recurring', methods=['POST'])
@login_required
def api_add_recurring():
    user_id = session['user_id']
    data = request.get_json() or {}
    success, result = add_recurring_expense(
        user_id=user_id,
        name=data.get('name'),
        category_id=data.get('category_id'),
        amount=data.get('amount'),
        frequency=data.get('frequency'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Recurring bill saved successfully.', 'data': result}), 201

@recurring_bp.route('/api/recurring/<int:recurring_id>', methods=['DELETE'])
@login_required
def api_delete_recurring(recurring_id):
    user_id = session['user_id']
    success, result = delete_recurring_expense(user_id, recurring_id)
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': result})
