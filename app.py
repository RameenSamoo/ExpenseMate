import os
from flask import Flask, jsonify, session
from config import Config
from database.database import init_db

def create_app(config_class=Config):
    app = Flask(__name__,
                template_folder=os.path.join('frontend', 'templates'),
                static_folder=os.path.join('frontend', 'static'))
    app.config.from_object(config_class)

    # Initialize Database Tables
    with app.app_context():
        init_db()

    # Register Route Blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.income_routes import income_bp
    from routes.expense_routes import expense_bp
    from routes.transaction_routes import transaction_bp
    from routes.budget_routes import budget_bp
    from routes.goal_routes import goal_bp
    from routes.analytics_routes import analytics_bp
    from routes.category_routes import category_bp
    from routes.recurring_routes import recurring_bp
    from routes.reports_routes import reports_bp
    from routes.settings_routes import settings_bp
    from routes.csv_routes import csv_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(goal_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(recurring_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(csv_bp)

    # Global Error Handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'success': False, 'message': 'Bad Request.'}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'success': False, 'message': 'Unauthorized access.'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'success': False, 'message': 'Access forbidden.'}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'message': 'Requested resource not found.'}), 404

    @app.errorhandler(409)
    def conflict(e):
        return jsonify({'success': False, 'message': 'Resource conflict.'}), 409

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
