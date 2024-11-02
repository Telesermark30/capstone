#patient_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user, login_user
from models import Patient, Nutritionist, db
from flask_babel import _
from werkzeug.security import generate_password_hash

patient_bp = Blueprint('patient', __name__)

#patient basic info
@patient_bp.route('/basic_info', methods=['GET', 'POST'])
@login_required
def basic_info():
    patient_id = session.get('patient_id')
    if not patient_id:
        flash("Please log in to access this page.")
        return redirect(url_for('patient_login'))
    
    patient = Patient.query.get(patient_id)
    if request.method == 'POST':
        # Update patient info
        patient.weight = request.form['weight']
        patient.height = request.form['height']
        db.session.commit()
        
        # Update user information in the session
        session['user_info'] = {
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'sex': patient.sex,
            'age': patient.age,
            'email': patient.email,
            'username': patient.username,
            'password_hash': patient.password_hash,
            'weight': patient.weight,
            'height': patient.height
        }

        flash('Information updated successfully!')
        # Check the age group stored in the session
        age_group = session.get('age_group')
        print(f"Age Group: {age_group}")  # Debugging
        
        # Redirect to the appropriate questionnaire based on age group
        if age_group == "adolescent":  # Redirect if age group is for adolescents
            return redirect(url_for('stamp_questionnaire', step=1))
        else:
            return redirect(url_for('nutritional_screening', question_num=1, lang=session.get('language', 'en')))
    
    language = session.get('language', 'en')
    translations = {
        'en': {
            'title': 'Enter Basic Information',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'sex': 'Sex',
            'male': 'Male',
            'female': 'Female',
            'age': 'Age',
            'weight': 'Weight (kg)',
            'height': 'Height (cm)',
            'next_button': 'Next'
        },
        'ceb': {
            'title': 'Ibutang ang Imong Impormasyon',
            'first_name': 'Pangalan',
            'last_name': 'Apelyido',
            'sex': 'Kasarian',
            'male': 'Lalaki',
            'female': 'Babae',
            'age': 'Edad',
            'weight': 'Timbang (kg)',
            'height': 'Taas (cm)',
            'next_button': 'Sunod'
        }
    }
    translated_text = translations.get(language, translations['en'])

    return render_template(
        'basic_info.html',
        first_name=patient.first_name,
        last_name=patient.last_name,
        sex=patient.sex,
        age=patient.age,
        weight=patient.weight,
        height=patient.height,
        title=translated_text['title'],
        next_button=translated_text['next_button'],
        translated_text=translated_text
    )


@patient_bp.route('/select_nutritionist', methods=['GET', 'POST'])
def select_nutritionist():
    nutritionists = Nutritionist.query.all()
    if request.method == 'POST':
        selected_nutritionist_id = request.form.get('nutritionist_id')
        if not selected_nutritionist_id:
            flash(_('Please select a nutritionist.'))
            return redirect(url_for('patient.select_nutritionist'))
        session['selected_nutritionist_id'] = selected_nutritionist_id
        return redirect(url_for('patient.patient_login'))
    return render_template('select_nutritionist.html', nutritionists=nutritionists)

@patient_bp.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt with username: {username}")  # Debug prompt
        
        patient = Patient.query.filter_by(username=username).first()

        if patient:
            print(f"Username found: {username}")  # Debug prompt
            if patient.check_password(password):
                login_user(patient)
                session['patient_id'] = patient.id
                print(f"User {username} logged in successfully.")  # Debug prompt
                return redirect(url_for('questionnaire.select_age_group'))
            else:
                print(f"Invalid password for username: {username}")  # Debug prompt
                flash(_('Invalid username or password.'))
        else:
            print(f"Invalid username: {username}")  # Debug prompt
            flash(_('Invalid username or password.'))
            
        return redirect(url_for('patient.patient_login'))
    return render_template('patient_login.html')

def validate_patient_data(age, selected_age_group):
    # Helper function to verify age group consistency
    if 13 <= age <= 19 and selected_age_group != 'adolescent':
        return "Age does not match the adolescent group."
    if 20 <= age <= 59 and selected_age_group != 'adult':
        return "Age does not match the adult group."
    if age >= 60 and selected_age_group != 'senior':
        return "Age does not match the senior group."
    return None

@patient_bp.route('/create_patient_account', methods=['GET', 'POST'])
def create_patient_account():
    if request.method == 'POST':
        try:
            # Validate age and group
            age = int(request.form.get('age', 0))
            selected_age_group = request.form.get('age_group')
            error = validate_patient_data(age, selected_age_group)
            if error:
                flash(error, 'danger')
                return redirect(url_for('patient.create_patient_account'))

            # Collect and validate form data
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'sex', 'age', 'height', 'weight']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f"{field.replace('_', ' ').capitalize()} is required.", 'danger')
                    return redirect(url_for('patient.create_patient_account'))

            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            sex = request.form['sex']
            height = float(request.form['height'])
            weight = float(request.form['weight'])

            # Define age group
            age_group = 'adolescent' if 13 <= age <= 19 else 'adult' if 20 <= age <= 59 else 'senior'
            if age_group != selected_age_group:
                flash('Age does not match the selected age group. Please correct.', 'danger')
                return redirect(url_for('patient.create_patient_account'))

            # Check if username and email are unique
            if Patient.query.filter_by(username=username).first():
                flash('Username already exists.', 'danger')
                return redirect(url_for('patient.create_patient_account'))
            if Patient.query.filter_by(email=email).first():
                flash('Email already exists.', 'danger')
                return redirect(url_for('patient.create_patient_account'))

            # Create and save new patient
            new_patient = Patient(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                sex=sex,
                age=age,
                height=height,
                weight=weight,
                age_group=age_group
            )
            db.session.add(new_patient)
            db.session.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('patient.patient_login'))

        except Exception as e:
            db.session.rollback()  # Ensure rollback on error
            flash(f'An error occurred: {str(e)}', 'danger')
    return render_template('create_patient_account.html')




#patient forget password
@patient_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Look for the patient in the database by email
        patient = Patient.query.filter_by(email=email).first()

        if patient:
            # Normally you would generate a secure token and send an email with the reset link
            # For simplicity, we just flash a success message for now
            flash('Password reset link has been sent to your email.', 'success')
            # Here you would actually send the email using something like Flask-Mail

        else:
            flash('Email not found. Please check and try again.', 'danger')

    return render_template('forgot_password.html')
