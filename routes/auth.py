import random
import string
from datetime import datetime, timedelta
from config.email import send_verification_email
from config.sms import send_verification_sms
from flask import Blueprint, json, request, jsonify
from config.db import get_db_connection
import bcrypt
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)


# ─── REGISTER ───────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    password = data.get('password')
    role = data.get('role', 'user')
    specialization = data.get('specialization')

    if not full_name or not email or not
