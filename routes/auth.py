import random
import string
from datetime import datetime, timedelta
from config.email import send_verification_email
from flask import Blueprint, json, request, jsonify
from config.sms import send_verification_sms
from config.db import get_db_connection
import bcrypt
from flask_jwt_extended import create_access_token

# blueprint below groups all auths routes  under one name
auth_bp = Blueprint('auth', __name__)

# Register route
@auth_bp.route('/register', methods=['POST'])
def register():
    
    # Get the dta the user sent
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    password = data.get('password')
    role = data.get('role', 'user')
    
    
    # ensure nothing is missing
    if not full_name or not email or not phone_number or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    #make sure role is valid
    if role not in ['user', 'mechanic']:
        return jsonify({'error': 'role must be user or mechanic'}), 400
    
    
    #encrypt the password
    password_hash =bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Generate a 6 digit code
    code = ''.join(random.choices(string .digits, k=6))
    expires = datetime.utcnow() + timedelta(minutes=10)
    
    #save the user to the database
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        #check if email already exists
        cur.execute('SELECT id FROM users WHERE email = %s', (email,))
        existing_user = cur.fetchone()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        #add the new user
        cur.execute('''
        INSERT INTO users (full_name, email, phone_number, password_hash, role, is_verified, verification_code, verification_expires)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        ''', (full_name, email, phone_number, password_hash, role, False, code, expires))
        
        new_user_id = cur.fetchone()[0]
        
        #if use mechanic create their profile 
        if role == 'mechanic':
            cur.execute('''
                        INSERT INTO mechanic_profiles(user_id, is_active)
                        VALUES (%s, %s)
                        ''', (new_user_id, False))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # send verification code via email and SMS
        try:
            send_verification_email(full_name,email, code)
        except Exception as e:
            print(f"Failed to send verification email: {e}")
        
        try:
            send_verification_sms(phone_number, code)
        except Exception as e:
            print(f"Failed to send verification SMS: {e}")
        
        return jsonify({
            'message': 'Account registered. Please verify your email and phone number.'
            }), 201
        # send verification code via email and SMS
        print(f"Attempting to send email to: {email}")
        print(f"Attempting to send SMS to: {phone_number}")
        print(f"Verification code: {code}")

        try:
        send_verification_email(full_name, email, code)
        print("Email sent successfully")
        except Exception as e:
        print(f"Email failed: {e}")

        try:
        send_verification_sms(phone_number, code)
        print("SMS sent successfully")
        except Exception as e:
        print(f"SMS failed: {e}")
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get everything in ONE query
        cur.execute('''
            SELECT id, full_name, role, password_hash, is_verified
            FROM users
            WHERE email = %s
        ''', (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        user_id = user[0]
        full_name = user[1]
        role = user[2]
        password_hash = user[3]
        is_verified = user[4]

        # Check verified
        if not is_verified:
            return jsonify({'error': 'Please verify your account first. Check your email and phone for the code.'}), 403

        # Check password
        password_match = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        if not password_match:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Create token
        token = create_access_token(identity=json.dumps({
            'id': str(user_id),
            'role': role
        }))

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user_id),
                'full_name': full_name,
                'role': role
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()   

@auth_bp.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if not email or not code:
        return jsonify({'error': 'Email and code are required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the user exists
        cur.execute('SELECT id FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_id = user[0]

        # Check if the code is valid and not expired
        cur.execute('SELECT verification_code, verification_expires FROM users WHERE id = %s', (user_id,))
        saved_code, expires = cur.fetchone()
        if saved_code != code:
            return jsonify({'error': 'Invalid verification code'}), 400
        
        if datetime.utcnow() > expires:
            return jsonify({'error': 'Verification code has expired. Please register again'}), 400 
        
        # Mark as verified
        cur.execute('''
                    UPDATE users
                    SET is_verified = TRUE,
                        verification_code = null,
                        verification_expires = null
                    WHERE id = %s
                    ''', (user_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Verification successful. Please log in'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
