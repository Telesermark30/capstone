# routes/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import Admin, Nutritionist, Patient, MnaResult, db
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash

admin_bp = Blueprint('admin', __name__)

# Admin dashboard and other routes remain the same
@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not isinstance(current_user, Admin):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('auth.login'))

    admin = Admin.query.filter_by(username=current_user.username).first()
    patients = Patient.query.options(joinedload(Patient.mna_result)).all()
    nutritionists = Nutritionist.query.all()

    # Filters for search and filtering options
    search_name = request.args.get('name')
    filter_age = request.args.get('age')
    filter_gender = request.args.get('sex')
    filter_status = request.args.get('status')

    # Apply filters if they exist
    if search_name:
        patients = patients.filter(Patient.first_name.contains(search_name) | Patient.last_name.contains(search_name))
    if filter_age:
        patients = patients.filter(Patient.age == int(filter_age))
    if filter_gender:
        patients = patients.filter(Patient.sex == filter_gender)
    if filter_status:
        patients = patients.filter(MnaResult.status == filter_status)

    return render_template('dashboard.html', patients=patients, admin_id=admin.id, nutritionists=nutritionists)

@admin_bp.route('/update_admin/<int:admin_id>', methods=['POST'])
@login_required
def update_admin(admin_id):
    admin = db.session.get(Admin, admin_id)
    if request.method == 'POST':
        admin.username = request.form['username']
        if request.form['password']:
            admin.set_password(request.form['password'])  # Set new password if provided
        db.session.commit()
        flash('Admin updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('update_admin.html', admin=admin)

@admin_bp.route('/delete_admin/<int:admin_id>', methods=['POST'])
@login_required
def delete_admin(admin_id):
    try:
        admin = db.session.get(Admin, admin_id)
        if admin:
            db.session.delete(admin)
            db.session.commit()
            flash('Admin deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting admin. Please try again.', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/update_nd/<int:nd_id>', methods=['POST'])
@login_required
def update_nd(nd_id):
    nd = db.session.get(Nutritionist, nd_id)

    # Update ND details
    nd.first_name = request.form['first_name']
    nd.last_name = request.form['last_name']
    nd.email = request.form['email']
    nd.phone_number = request.form['phone_number']
    nd.username = request.form['username']

    # Update the password if a new one is provided
    if request.form['password']:
        nd.password_hash = generate_password_hash(request.form['password'])

    db.session.commit()

    flash('Nutritionist/Dietitian updated successfully!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/delete_nd/<int:nd_id>', methods=['POST'])
@login_required
def delete_nd(nd_id):
    nd = db.session.get(Nutritionist, nd_id)
    if nd:
        db.session.delete(nd)
        db.session.commit()
        flash('Nutritionist/Dietitian deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


# Route to create a new admin from the dashboard
@admin_bp.route('/add_admin', methods=['POST'])
@login_required
def add_admin():
    # Only allow the logged-in admin to add a new admin
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    username = request.form['username']
    password = request.form['password']

    # Check if the username already exists
    existing_admin = Admin.query.filter_by(username=username).first()
    if existing_admin:
        flash('Username already exists. Please choose a different username.', 'danger')
        return redirect(url_for('admin.dashboard'))

    # Create new admin
    new_admin = Admin(username=username)
    new_admin.set_password(password)  # Hash the password
    db.session.add(new_admin)
    db.session.commit()

    flash('New admin added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/add_nd', methods=['POST'])
@login_required
def add_nd():
    # Only allow the logged-in admin to add a new ND
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone_number = request.form['phone_number']
    username = request.form['username']
    password = request.form['password']

    # Check if the username or email already exists
    existing_nd = Nutritionist.query.filter(
        (Nutritionist.username == username) | (Nutritionist.email == email)
    ).first()
    if existing_nd:
        flash('Username or email already exists. Please choose a different one.', 'danger')
        return redirect(url_for('admin.dashboard'))

    # Hash the password
    password_hash = generate_password_hash(password)

    # Create new ND entry
    new_nd = Nutritionist(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        username=username,
        password_hash=password_hash
    )
    db.session.add(new_nd)
    db.session.commit()

    flash('New Nutritionist/Dietitian added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

 #Nutritionist dashboard
@admin_bp.route('/nd_dashboard')
@login_required
def nd_dashboard():
    if isinstance(current_user, Nutritionist):
        patients = Patient.query.filter_by(nutritionist_id=current_user.id).all()
        return render_template('nd_dashboard.html', patients=patients)
    else:
        flash("Unauthorized access to Nutritionist Dashboard.", "danger")
        return redirect(url_for('auth.login'))



    