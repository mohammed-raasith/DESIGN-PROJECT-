from flask import Blueprint, jsonify, render_template
from app import db
from db.models import Alert

alert_bp = Blueprint('alert', __name__)

@alert_bp.route('/alerts')
def alerts_view():
    return render_template('alerts.html')

@alert_bp.route('/api/alerts', methods=['GET'])
def get_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
    result = [{
        'id': a.id,
        'alert_type': a.alert_type,
        'item_id': a.item_id,
        'severity': a.severity,
        'message': a.message,
        'timestamp': a.timestamp.isoformat()
    } for a in alerts]
    
    return jsonify(result), 200
