import os
import json
from datetime import datetime
from functools import wraps
from flask import request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')


def _read_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('users', []) if isinstance(data, dict) else []
    except Exception:
        return []


def _write_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users': users}, f, indent=2)


def _get_serializer(secret_key: str):
    return URLSafeTimedSerializer(secret_key, salt='auth-token')


def create_token(secret_key: str, payload: dict, expires_in: int = 60 * 60 * 8):
    s = _get_serializer(secret_key)
    # Put expiry inside payload for client info; serializer will enforce via max_age
    payload = dict(payload)
    payload['exp'] = int(datetime.utcnow().timestamp()) + expires_in
    return s.dumps(payload)


def verify_token(secret_key: str, token: str):
    s = _get_serializer(secret_key)
    try:
        data = s.loads(token, max_age=60 * 60 * 24)  # hard cap 24h
        return data
    except SignatureExpired:
        return None
    except BadSignature:
        return None


def find_user_by_email(email: str):
    users = _read_users()
    return next((u for u in users if u.get('email') == email), None)


def register_user(email: str, password: str):
    email = (email or '').strip().lower()
    if not email or '@' not in email:
        return False, 'Invalid email'
    if not password or len(password) < 6:
        return False, 'Password must be at least 6 characters'
    users = _read_users()
    if any(u.get('email') == email for u in users):
        return False, 'Email already registered'
    user = {
        'id': f'u{len(users)+1:05d}',
        'email': email,
        'password_hash': generate_password_hash(password),
        'created_at': datetime.utcnow().isoformat()
    }
    users.append(user)
    _write_users(users)
    return True, {'id': user['id'], 'email': user['email']}


def authenticate_user(email: str, password: str):
    user = find_user_by_email((email or '').strip().lower())
    if not user:
        return False, 'Invalid credentials'
    if not check_password_hash(user.get('password_hash', ''), password or ''):
        return False, 'Invalid credentials'
    return True, {'id': user['id'], 'email': user['email']}


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        token = auth_header.split(' ', 1)[1]
        payload = verify_token(os.environ.get('SECRET_KEY', 'dev-secret'), token)
        if not payload:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        g.user = {'id': payload.get('id'), 'email': payload.get('email')}
        return fn(*args, **kwargs)
    return wrapper
