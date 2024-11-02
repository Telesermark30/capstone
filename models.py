# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Admin Model
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    # Set password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check password against hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Nutritionist Model
class Nutritionist(UserMixin, db.Model):
    __tablename__ = 'nutritionists'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now())

    # Set password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check password against hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Patient Model
class Patient(UserMixin, db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    sex = db.Column(db.String(10))
    nutritionist_id = db.Column(db.Integer, db.ForeignKey('nutritionists.id'))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    age_group = db.Column(db.String(20))

    # Relationships
    nutritionist = db.relationship('Nutritionist', backref='patients')

    # Set password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check password against hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Stamp Result Model
class StampResult(db.Model):
    __tablename__ = 'stamp_results'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    total_score = db.Column(db.Integer)
    risk_level = db.Column(db.String(50))
    care_plan = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    # Relationships
    patient = db.relationship('Patient', backref='stamp_results')


# SGA Result Model
class SGAResult(db.Model):
    __tablename__ = 'sga_results'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    total_score = db.Column(db.Integer, nullable=False)
    assessment = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    # Relationships
    patient = db.relationship('Patient', backref='sga_results')


# MNA Result Model
class MnaResult(db.Model):
    __tablename__ = 'mna_result'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), unique=True)  # Enforces one-to-one relationship
    status = db.Column(db.String(50))

    # Relationships
    patient = db.relationship('Patient', backref=db.backref('mna_result', uselist=False))
