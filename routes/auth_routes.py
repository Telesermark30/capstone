# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from models import Admin, Nutritionist, db
from werkzeug.security import check_password_hash
from datetime import timedelta
import mysql.connector

auth_bp = Blueprint('auth', __name__)

# Login route handling both admin and nutritionist
# routes/auth_routes.py
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        user = None
        if user_type == 'admin':
            user = Admin.query.filter_by(username=username).first()
        elif user_type == 'nutritionist':
            user = Nutritionist.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"{user_type.capitalize()} login successful!", "success")
            if user_type == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('admin.nd_dashboard'))
        else:
            flash(f'Invalid {user_type} username or password.', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))


# Route to create a new admin - restricted access
@auth_bp.route('/create_admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    if not isinstance(current_user, Admin):  # Only allow Admin users to access this route
        flash("Access restricted to admins only.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('auth.create_admin'))

        # Create the new admin
        new_admin = Admin(username=username)
        new_admin.set_password(password)  # Hash the password
        db.session.add(new_admin)
        db.session.commit()

        flash('New admin created successfully!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('create_admin.html')

@auth_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        print("Admin fetched:", admin)  # Debug

        if admin and admin.check_password(password):
            login_user(admin)
            flash("Admin login successful!", "success")
            return redirect(url_for('admin.dashboard'))
        else:
            print("Login failed: Invalid credentials")  # Debug
            flash('Invalid admin username or password.', 'danger')

    return render_template('admin_login.html')



@auth_bp.route('/nd_login', methods=['GET', 'POST'])
def nd_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nutritionist = Nutritionist.query.filter_by(username=username).first()

        if nutritionist and nutritionist.check_password(password):
            login_user(nutritionist)
            flash("Nutritionist login successful!", "success")
            return redirect(url_for('admin.nd_dashboard'))
        else:
            flash('Invalid nutritionist username or password.', 'danger')

    return render_template('nd_login.html')
