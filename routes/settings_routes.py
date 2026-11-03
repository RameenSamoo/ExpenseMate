from flask import Blueprint, request, jsonify, render_template, session
from services.auth_service import get_user_by_id, update_user_profile
from utils.decorators import login_required

settings_bp = Blueprint('settings_routes', __name__)

@settings_bp.route('/settings', methods=['GET'])
@login_required
def settings_view():
    return render_template('settings.html', user_name=session.get('full_name', 'User'))

@settings_bp.route('/api/settings', methods=['GET'])
@login_required
def api_get_settings():
    user = get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User profile not found.'}), 404
    return jsonify({'success': True, 'user': user})

@settings_bp.route('/api/settings', methods=['PUT'])
@login_required
def api_update_settings():
    user_id = session['user_id']
    data = request.get_json() or {}

    success, result = update_user_profile(
        user_id=user_id,
        full_name=data.get('full_name'),
        email=data.get('email'),
        currency=data.get('currency'),
        current_password=data.get('current_password'),
        new_password=data.get('new_password')
    )

    if not success:
        return jsonify({'success': False, 'message': result}), 400

    if isinstance(result, dict):
        session['full_name'] = result['full_name']
        session['email'] = result['email']

    return jsonify({'success': True, 'message': 'Profile updated successfully.', 'user': result})
