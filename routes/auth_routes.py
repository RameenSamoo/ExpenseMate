from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from services.auth_service import register_user, login_user, get_user_by_id
from utils.decorators import login_required

auth_bp = Blueprint('auth_routes', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_view():
    if 'user_id' in session:
        return redirect(url_for('dashboard_routes.dashboard_view'))
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET'])
def register_view():
    if 'user_id' in session:
        return redirect(url_for('dashboard_routes.dashboard_view'))
    return render_template('register.html')

@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    success, result = register_user(
        data.get('full_name'),
        data.get('email'),
        data.get('password'),
        data.get('confirm_password')
    )
    if not success:
        return jsonify({'success': False, 'message': result}), 400

    session['user_id'] = result['id']
    session['full_name'] = result['full_name']
    session['email'] = result['email']
    return jsonify({'success': True, 'message': 'Registration successful.', 'user': result}), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    success, result = login_user(data.get('email'), data.get('password'))
    if not success:
        return jsonify({'success': False, 'message': result}), 401

    session['user_id'] = result['id']
    session['full_name'] = result['full_name']
    session['email'] = result['email']
    return jsonify({'success': True, 'message': 'Login successful.', 'user': result})

@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})

@auth_bp.route('/logout', methods=['GET'])
def logout_view():
    session.clear()
    return redirect(url_for('auth_routes.login_view'))

@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def api_me():
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'success': False, 'message': 'User not found.'}), 404
    return jsonify({'success': True, 'user': user})
