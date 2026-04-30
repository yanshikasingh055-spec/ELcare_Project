from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patient_profile = db.relationship('PatientProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    predictions = db.relationship('PredictionHistory', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class PatientProfile(db.Model):
    __tablename__ = 'patient_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # Personal Info
    full_name = db.Column(db.String(150))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    phone = db.Column(db.String(20))

    # Medical Info
    blood_group = db.Column(db.String(10))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    allergies = db.Column(db.Text)
    existing_conditions = db.Column(db.Text)
    medications = db.Column(db.Text)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def bmi(self):
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 1)
        return None

    def __repr__(self):
        return f'<PatientProfile user_id={self.user_id}>'


class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    disease_type = db.Column(db.String(50), nullable=False)   # 'diabetes', 'heart', 'parkinsons'
    input_features = db.Column(db.Text, nullable=False)       # JSON string of input values
    prediction_result = db.Column(db.Integer, nullable=False) # 0 or 1
    result_message = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction {self.disease_type} user={self.user_id} result={self.prediction_result}>'
