from flask import Blueprint, request, jsonify, render_template, session
from services.goal_service import (
    add_goal, update_goal, delete_goal, get_goals, get_goal_by_id,
    add_goal_contribution, delete_goal_contribution, get_goal_contributions
)
from utils.decorators import login_required

goal_bp = Blueprint('goal_routes', __name__)

@goal_bp.route('/goals', methods=['GET'])
@login_required
def goals_view():
    return render_template('goals.html', user_name=session.get('full_name', 'User'))

@goal_bp.route('/api/goals', methods=['GET'])
@login_required
def api_get_goals():
    user_id = session['user_id']
    data = get_goals(user_id)
    return jsonify({'success': True, 'data': data})

@goal_bp.route('/api/goals/<int:goal_id>', methods=['GET'])
@login_required
def api_get_goal_by_id(goal_id):
    user_id = session['user_id']
    goal = get_goal_by_id(user_id, goal_id)
    if not goal:
        return jsonify({'success': False, 'message': 'Goal not found.'}), 404
    return jsonify({'success': True, 'data': goal})

@goal_bp.route('/api/goals', methods=['POST'])
@login_required
def api_add_goal():
    user_id = session['user_id']
    data = request.get_json() or {}
    success, result = add_goal(
        user_id=user_id,
        goal_name=data.get('goal_name'),
        start_date=data.get('start_date'),
        target_date=data.get('target_date'),
        target_amount=data.get('target_amount'),
        starting_amount=data.get('starting_amount', 0.0),
        monthly_target=data.get('monthly_target', 0.0),
        priority=data.get('priority', 'Medium'),
        notes=data.get('notes', '')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Financial goal created successfully.', 'data': result}), 201

@goal_bp.route('/api/goals/<int:goal_id>', methods=['PUT'])
@login_required
def api_update_goal(goal_id):
    user_id = session['user_id']
    data = request.get_json() or {}
    success, result = update_goal(
        user_id=user_id,
        goal_id=goal_id,
        goal_name=data.get('goal_name'),
        start_date=data.get('start_date'),
        target_date=data.get('target_date'),
        target_amount=data.get('target_amount'),
        starting_amount=data.get('starting_amount'),
        monthly_target=data.get('monthly_target'),
        priority=data.get('priority'),
        notes=data.get('notes')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Goal updated successfully.', 'data': result})

@goal_bp.route('/api/goals/<int:goal_id>', methods=['DELETE'])
@login_required
def api_delete_goal(goal_id):
    user_id = session['user_id']
    success, result = delete_goal(user_id, goal_id)
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': result})

@goal_bp.route('/api/goals/<int:goal_id>/contributions', methods=['GET'])
@login_required
def api_get_contributions(goal_id):
    user_id = session['user_id']
    result = get_goal_contributions(user_id, goal_id)
    if result is None:
        return jsonify({'success': False, 'message': 'Goal not found.'}), 404
    return jsonify({'success': True, 'data': result})

@goal_bp.route('/api/goals/<int:goal_id>/contributions', methods=['POST'])
@login_required
def api_add_contribution(goal_id):
    user_id = session['user_id']
    data = request.get_json() or {}
    success, result = add_goal_contribution(
        user_id=user_id,
        goal_id=goal_id,
        amount=data.get('amount'),
        contribution_date=data.get('contribution_date'),
        description=data.get('description', '')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Goal contribution recorded successfully.', 'data': result}), 201

@goal_bp.route('/api/goals/contributions/<int:contribution_id>', methods=['DELETE'])
@login_required
def api_delete_contribution(contribution_id):
    user_id = session['user_id']
    success, result = delete_goal_contribution(user_id, contribution_id)
    if not success:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({'success': True, 'message': 'Contribution deleted successfully.', 'data': result})
