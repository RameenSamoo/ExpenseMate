from flask import Blueprint, request, jsonify, render_template, session
from services.category_service import get_user_categories, add_category, update_category, delete_category
from utils.decorators import login_required

category_bp = Blueprint('category_routes', __name__)

@category_bp.route('/categories', methods=['GET'])
@login_required
def categories_view():
    return render_template('categories.html', user_name=session.get('full_name', 'User'))

@category_bp.route('/api/categories', methods=['GET'])
@login_required
def api_get_categories():
    user_id = session['user_id']
    cat_type = request.args.get('type')
    categories = get_user_categories(user_id, category_type=cat_type)
    return jsonify({'success': True, 'data': categories})

@category_bp.route('/api/categories', methods=['POST'])
@login_required
def api_add_category():
    user_id = session['user_id']
    data = request.get_json() or {}
    success, result = add_category(
        user_id=user_id,
        name=data.get('name'),
        category_type=data.get('type')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Category created successfully.', 'data': result}), 201

@category_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
@login_required
def api_update_category(category_id):
    user_id = session['user_id']
    data = request.get_json() or {}
    success, result = update_category(
        user_id=user_id,
        category_id=category_id,
        new_name=data.get('name')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Category updated successfully.', 'data': result})

@category_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
@login_required
def api_delete_category(category_id):
    user_id = session['user_id']
    success, result = delete_category(user_id, category_id)
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': result})
