from flask import Blueprint, json, request, jsonify
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
        INSERT INTO users (full_name, email, phone_number, password_hash, role)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
        ''', (full_name, email, phone_number, password_hash, role))
        
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
        
        return jsonify({'message': 'Account registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#login route
@auth_bp.route('/login', methods=['POST'])
def login():
    
    #get the data the user sends
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT id, full_name, role, password_hash FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user_id = user[0]
        full_name = user[1]
        role = user[2]
        password_hash = user[3]
        
        
        #check if password is correct
        password_match = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))    
        if not password_match:
            return jsonify({'error': 'Invalid password'}), 401    
        
        #create a JWT token
        token = create_access_token(identity=json.dumps({
            'id': str(user_id),
            'role': role
        }))
        
        #send back the token and user info
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