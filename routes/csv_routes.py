from flask import Blueprint, request, jsonify, Response, session
from services.csv_service import export_transactions_csv, import_transactions_csv
from utils.decorators import login_required
import datetime

csv_bp = Blueprint('csv_routes', __name__)

@csv_bp.route('/api/export', methods=['GET'])
@login_required
def api_export_csv():
    user_id = session['user_id']
    tx_type = request.args.get('type')
    category_id = request.args.get('category_id')
    month = request.args.get('month')
    year = request.args.get('year')

    csv_data = export_transactions_csv(user_id, transaction_type=tx_type, category_id=category_id, month=month, year=year)
    filename = f"expensemate_transactions_{datetime.date.today().strftime('%Y%m%d')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@csv_bp.route('/api/import', methods=['POST'])
@login_required
def api_import_csv():
    user_id = session['user_id']

    if 'file' in request.files:
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'success': False, 'message': 'No CSV file provided.'}), 400
        csv_text = file.read().decode('utf-8-sig', errors='replace')
    else:
        csv_text = request.get_data(as_text=True)

    success, result = import_transactions_csv(user_id, csv_text)
    if not success:
        return jsonify({'success': False, 'message': result}), 400

    return jsonify({
        'success': True,
        'message': f"CSV Import complete. {result['imported']} transactions imported, {result['rejected']} rejected.",
        'summary': result
    })
