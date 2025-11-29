from flask import Blueprint, request, jsonify

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    return jsonify({'message': 'Login endpoint', 'user_id': 1})

@bp.route('/register', methods=['POST'])
def register():
    return jsonify({'message': 'Register endpoint', 'user_id': 1})