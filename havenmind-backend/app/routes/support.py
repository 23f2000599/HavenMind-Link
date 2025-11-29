from flask import Blueprint, request, jsonify

bp = Blueprint('support', __name__, url_prefix='/api/support')

@bp.route('/sessions', methods=['POST'])
def create_session():
    return jsonify({'message': 'Support session created', 'session_id': 1})

@bp.route('/messages', methods=['POST'])
def send_message():
    return jsonify({'message': 'Message sent'})