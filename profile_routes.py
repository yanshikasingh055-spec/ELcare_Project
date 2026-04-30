from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import db, PatientProfile, PredictionHistory
from datetime import datetime
import json

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@profile_bp.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    p = current_user.patient_profile
    if not p:
        return jsonify({'success': False, 'message': 'Profile not found'}), 404

    return jsonify({
        'success': True,
        'profile': {
            'full_name': p.full_name,
            'date_of_birth': p.date_of_birth.isoformat() if p.date_of_birth else None,
            'gender': p.gender,
            'phone': p.phone,
            'blood_group': p.blood_group,
            'height_cm': p.height_cm,
            'weight_kg': p.weight_kg,
            'bmi': p.bmi,
            'allergies': p.allergies,
            'existing_conditions': p.existing_conditions,
            'medications': p.medications,
        }
    })


@profile_bp.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()
    p = current_user.patient_profile

    if not p:
        p = PatientProfile(user_id=current_user.id)
        db.session.add(p)

    p.full_name = data.get('full_name', p.full_name)
    p.gender = data.get('gender', p.gender)
    p.phone = data.get('phone', p.phone)
    p.blood_group = data.get('blood_group', p.blood_group)
    p.height_cm = data.get('height_cm', p.height_cm)
    p.weight_kg = data.get('weight_kg', p.weight_kg)
    p.allergies = data.get('allergies', p.allergies)
    p.existing_conditions = data.get('existing_conditions', p.existing_conditions)
    p.medications = data.get('medications', p.medications)

    dob = data.get('date_of_birth')
    if dob:
        try:
            p.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            pass

    p.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'message': 'Profile updated!', 'bmi': p.bmi})


@profile_bp.route('/history')
@login_required
def history():
    return render_template('history.html', user=current_user)


@profile_bp.route('/api/history', methods=['GET'])
@login_required
def get_history():
    disease = request.args.get('disease')  # optional filter
    query = PredictionHistory.query.filter_by(user_id=current_user.id)

    if disease:
        query = query.filter_by(disease_type=disease)

    records = query.order_by(PredictionHistory.created_at.desc()).all()

    history_list = []
    for r in records:
        try:
            features = json.loads(r.input_features)
        except Exception:
            features = {}
        history_list.append({
            'id': r.id,
            'disease_type': r.disease_type,
            'input_features': features,
            'prediction_result': r.prediction_result,
            'result_message': r.result_message,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    return jsonify({'success': True, 'history': history_list})


@profile_bp.route('/api/history/<int:record_id>', methods=['DELETE'])
@login_required
def delete_history(record_id):
    record = PredictionHistory.query.filter_by(id=record_id, user_id=current_user.id).first()
    if not record:
        return jsonify({'success': False, 'message': 'Record not found'}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Record deleted'})
