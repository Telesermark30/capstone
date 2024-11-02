from flask import Flask, render_template, session, redirect, url_for, flash, request
from config import Config
from models import db, Admin, Nutritionist, Patient  # Import Admin, Nutritionist, and Patient models here
from flask_session import Session
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.admin_routes import admin_bp
from routes.questionnaire_routes import questionnaire_bp
from routes.util_routes import util_bp
from flask_babel import Babel
from datetime import timedelta

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(minutes=30)
Session(app)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
babel = Babel(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(patient_bp, url_prefix='/patient')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(questionnaire_bp, url_prefix='/questionnaire')
app.register_blueprint(util_bp, url_prefix='/util')

# Database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'your_database'
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/your_database'

# User Loader for Login Manager

@login_manager.user_loader
def load_user(user_id):
    # Attempt to retrieve Admin, Nutritionist, or Patient based on the user_id
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
    nutritionist = Nutritionist.query.get(int(user_id))
    if nutritionist:
        return nutritionist
    return Patient.query.get(int(user_id))


# Global access restriction function
@app.before_request
def restrict_access():
    allowed_routes = ['auth.login', 'auth.register', 'static', 'home']
    
    # Redirect unauthorized users to the login page
    if not current_user.is_authenticated and request.endpoint not in allowed_routes:
        return redirect(url_for('auth.login'))

    # Redirect non-admin users from admin routes
    if request.blueprint == 'admin' and not isinstance(current_user, Admin):
        flash("Admins only.", "danger")
        return redirect(url_for('auth.login'))
    
    # Redirect non-nutritionist users from nutritionist routes
    if request.blueprint == 'nd' and not isinstance(current_user, Nutritionist):
        flash("Nutritionists only.", "danger")
        return redirect(url_for('auth.login'))

# Locale selector function to retrieve the language from the session
def get_locale():
    return session.get('language', 'en')

@app.route('/')
def home():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    db.session.rollback()
    flash('An unexpected error occurred. Please try again.', 'danger')
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
