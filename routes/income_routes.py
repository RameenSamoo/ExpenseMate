from flask import Blueprint, request, jsonify, render_template, session
from services.transaction_service import add_transaction, update_transaction, delete_transaction, get_transactions, get_transaction_by_id
from services.analytics_service import get_income_analytics
from utils.decorators import login_required

income_bp = Blueprint('income_routes', __name__)

@income_bp.route('/income', methods=['GET'])
@login_required
def income_view():
    return render_template('income.html', user_name=session.get('full_name', 'User'))

@income_bp.route('/api/income', methods=['GET'])
@login_required
def api_get_income():
    user_id = session['user_id']
    category_id = request.args.get('category_id')
    month = request.args.get('month')
    year = request.args.get('year')
    search = request.args.get('search')
    page = request.args.get('page', 1)
    limit = request.args.get('limit', 50)

    result = get_transactions(
        user_id=user_id,
        transaction_type='income',
        category_id=category_id,
        month=month,
        year=year,
        search=search,
        page=page,
        limit=limit
    )
    analytics = get_income_analytics(user_id, year=year)

    return jsonify({
        'success': True,
        'data': result,
        'analytics': analytics
    })

@income_bp.route('/api/income', methods=['POST'])
@login_required
def api_add_income():
    user_id = session['user_id']
    data = request.get_json() or {}
    success, result = add_transaction(
        user_id=user_id,
        category_id=data.get('category_id'),
        transaction_type='income',
        amount=data.get('amount'),
        description=data.get('description'),
        transaction_date=data.get('transaction_date'),
        payment_method=data.get('payment_method', 'Cash'),
        notes=data.get('notes', '')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Income record added successfully.', 'data': result}), 201

@income_bp.route('/api/income/<int:income_id>', methods=['PUT'])
@login_required
def api_update_income(income_id):
    user_id = session['user_id']
    data = request.get_json() or {}
    success, result = update_transaction(
        user_id=user_id,
        transaction_id=income_id,
        category_id=data.get('category_id'),
        amount=data.get('amount'),
        description=data.get('description'),
        transaction_date=data.get('transaction_date')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Income record updated successfully.', 'data': result})

@income_bp.route('/api/income/<int:income_id>', methods=['DELETE'])
@login_required
def api_delete_income(income_id):
    user_id = session['user_id']
    success, result = delete_transaction(user_id, income_id)
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': result})
