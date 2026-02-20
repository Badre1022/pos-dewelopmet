import os
from flask import Flask, render_template
from database import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.inventory import inventory_bp
    from routes.customers import customer_bp
    from routes.rentals import rental_bp
    from routes.reports import reports_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(rental_bp)
    app.register_blueprint(reports_bp)

    @app.route('/')
    def index():
        return render_template('base.html')

    with app.app_context():
        db.create_all()
        from werkzeug.security import generate_password_hash
        
        # Setup System Admin (Badre)
        admin_user = User.query.filter_by(username='Badre').first()
        if not admin_user:
            admin_user = User(username='Badre')
            db.session.add(admin_user)
        admin_user.role = 'admin'
        admin_user.password_hash = generate_password_hash('Badre.1230')
        
        # Setup Cashier (admin) - confusing name but per requirements
        cashier_user = User.query.filter_by(username='admin').first()
        if not cashier_user:
            cashier_user = User(username='admin')
            db.session.add(cashier_user)
        cashier_user.role = 'cashier'
        cashier_user.password_hash = generate_password_hash('admin.123')
        
        db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
