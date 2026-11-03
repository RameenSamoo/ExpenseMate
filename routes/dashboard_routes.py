from flask import Blueprint, request, jsonify, render_template, session
from services.analytics_service import get_dashboard_summary
from utils.decorators import login_required

dashboard_bp = Blueprint('dashboard_routes', __name__)

@dashboard_bp.route('/', methods=['GET'])
@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_view():
    return render_template('dashboard.html', user_name=session.get('full_name', 'User'))

@dashboard_bp.route('/api/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    user_id = session['user_id']
    month = request.args.get('month')
    year = request.args.get('year')
    data = get_dashboard_summary(user_id, month=month, year=year)
    return jsonify({'success': True, 'data': data})
