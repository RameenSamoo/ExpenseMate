from flask import Blueprint, request, jsonify, render_template, session
from services.transaction_service import get_transactions, get_transaction_by_id
from utils.decorators import login_required

transaction_bp = Blueprint('transaction_routes', __name__)

@transaction_bp.route('/transactions', methods=['GET'])
@login_required
def transactions_view():
    return render_template('transactions.html', user_name=session.get('full_name', 'User'))

@transaction_bp.route('/api/transactions', methods=['GET'])
@login_required
def api_get_transactions():
    user_id = session['user_id']
    tx_type = request.args.get('type')
    category_id = request.args.get('category_id')
    month = request.args.get('month')
    year = request.args.get('year')
    search = request.args.get('search')
    page = request.args.get('page', 1)
    limit = request.args.get('limit', 50)
    sort_by = request.args.get('sort_by', 'transaction_date')
    order = request.args.get('order', 'DESC')

    result = get_transactions(
        user_id=user_id,
        transaction_type=tx_type,
        category_id=category_id,
        month=month,
        year=year,
        search=search,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order
    )
    return jsonify({'success': True, 'data': result})

@transaction_bp.route('/api/transactions/<int:tx_id>', methods=['GET'])
@login_required
def api_get_transaction_by_id(tx_id):
    user_id = session['user_id']
    tx = get_transaction_by_id(user_id, tx_id)
    if not tx:
        return jsonify({'success': False, 'message': 'Transaction not found.'}), 404
    return jsonify({'success': True, 'data': tx})
