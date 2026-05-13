from flask import Blueprint, request, jsonify
from config.db import get_db_connection
from flask_jwt_extended import jwt_required
from decorators.admin_required import admin_required

admin_bp = Blueprint('admin', __name__)

#for users

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT id, full_name, email, phone_number, role, created_at
            FROM users
            ORDER BY created_at DESC
            ''')
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'full_name': row[1],
                'email': row[2],
                'phone_number': row[3],
                'role': row[4],
                'created_at': row[5].isoformat()
            })
        return jsonify({'users': users})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#delete a user    
@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM users WHERE id = %s::uuid', (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'User deleted'}),200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#For Garages
admin_bp.route('/garages', methods=['GET'])
@jwt_required()
@admin_required
def get_garages():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT g.id, g.name, g.phone_number, g.address, g.map_url, g.is_active,l.name AS location
            FROM garages g
            JOIN locations l ON g.location_id = l.id
            ORDER BY g.name
            ''')
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        garages = []
        for row in rows:
            garages.append({
                'id': row[0],
                'name': row[1],
                'phone_number': row[2],
                'address': row[3],
                'map_url': row[4],
                'is_active': row[5],
                'location': row[6]
            })
        return jsonify({'garages': garages})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
#adding a garage
@admin_bp.route('/garages', methods=['POST'])
@jwt_required()
@admin_required
def add_garage():
    data = request.get_json()
    name = data.get('name')
    location_id = data.get('location_id')
    phone_number = data.get('phone_number')
    address = data.get('address')
    map_url = data.get('map_url')
    
    if not name or not location_id or not phone_number:
        return jsonify({'error': 'Name, location_id and phone_number are required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO garages (name, location_id, phone_number, address, map_url, is_active)
            VALUES (%s, %s::uuid, %s, %s, %s, true)
            RETURNING id
            ''', (name, location_id, phone_number, address, map_url))
        
        garage_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Garage added', 'id': garage_id, 'Garage name': name}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#deleting a garage
@admin_bp.route('/garages/<garage_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_garage(garage_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM garages WHERE id = %s::uuid', (garage_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Garage deleted'}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#carwashes
@admin_bp.route('/carwashes', methods=['GET'])
@jwt_required()
@admin_required
def get_carwashes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT cw.id,
                     cw.name,
                     cw.phone_number,
                     cw.price,
                     cw.is_door_to_door,
                     cw.features,
                     cw.map_url,
                     cw.is_active,
                     l.name AS location
            FROM carwashes cw
            JOIN locations l ON cw.location_id = l.id
            ORDER BY cw.name
            ''')
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        carwashes = []
        for row in rows:
            carwashes.append({
                'id': row[0],
                'name': row[1],
                'phone_number': row[2],
                'price': float(row[3]),
                'is_door_to_door': row[4],
                'features': row[5],
                'map_url': row[6],
                'is_active': row[7],
                'location': row[8]
            })
        return jsonify({'carwashes': carwashes})
    except Exception as e:
            return jsonify({'error': str(e)}), 500
        
#adding a carwash
@admin_bp.route('/carwashes', methods=['POST'])
@jwt_required()
@admin_required
def add_carwash():
    data = request.get_json()
    name = data.get('name')
    location_id = data.get('location_id')
    phone_number = data.get('phone_number')
    price = data.get('price')
    is_door_to_door = data.get('is_door_to_door', False)
    features = data.get('features')
    map_url = data.get('map_url')
    
    if not name or not location_id or not phone_number or price is None:
        return jsonify({'error': 'Name, location_id, phone_number and price are required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO carwashes (name, location_id, phone_number, price, is_door_to_door, features, map_url, is_active)
            VALUES (%s, %s::uuid, %s, %s, %s, %s, %s, true)
            RETURNING id
            ''', (name, location_id, phone_number, price, is_door_to_door, features, map_url))
        
        carwash_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Carwash added', 'id': carwash_id}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#deleting a carwash
@admin_bp.route('/carwashes/<carwash_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_carwash(carwash_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM carwashes WHERE id = %s::uuid', (carwash_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Carwash deleted'}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#diagnostics
@admin_bp.route('/diagnostics', methods=['GET'])
@jwt_required()
@admin_required
def get_diagnostics():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT d.id,
                     d.name,
                     d.phone_number,
                     d.price_from,
                     d.features,
                     d.map_url,
                     d.is_active,
                        l.name AS location
            FROM diagnostics d
            JOIN locations l ON d.location_id = l.id
            ORDER BY d.name
            ''')
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        diagnostics = []
        for row in rows:
            diagnostics.append({
                'id': row[0],
                'name': row[1],
                'phone_number': row[2],
                'price_from': float(row[3]),
                'features': row[4],
                'map_url': row[5],
                'is_active': row[6],
                'location': row[7]
            })
        return jsonify({'diagnostics': diagnostics})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#adding a diagnostic
@admin_bp.route('/diagnostics', methods=['POST'])
@jwt_required()
@admin_required
def add_diagnostic():
    data = request.get_json()
    name = data.get('name')
    location_id = data.get('location_id')
    phone_number = data.get('phone_number')
    price_from = data.get('price_from')
    features = data.get('features')
    map_url = data.get('map_url')
    
    if not name or not location_id or not phone_number or price_from is None:
        return jsonify({'error': 'Name, location_id, phone_number and price_from are required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO diagnostics (name, location_id, phone_number, price_from, features, map_url, is_active)
            VALUES (%s, %s::uuid, %s, %s, %s, %s, true)
            RETURNING id
            ''', (name, location_id, phone_number, price_from, features, map_url))
        
        diagnostic_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Diagnostic added', 'id': diagnostic_id}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#deleteadiagnostic centre
@admin_bp.route('/diagnostics/<diagnostic_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_diagnostic(diagnostic_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM diagnostics WHERE id = %s::uuid', (diagnostic_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Diagnostic centre deleted'}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#get emergency providers
@admin_bp.route('/emergency_providers', methods=['GET'])
@jwt_required()
@admin_required
def get_emergency_providers():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT ep.id,
                     ep.name,
                     ep.phone_number,
                     ep.price,
                     ep.features,
                     ep.map_url,
                     ep.is_active,
                        l.name AS location
                        et.name AS emergency_type
            FROM emergency_providers ep
            JOIN locations l ON ep.location_id = l.id
            JOIN emergency_types et ON ep.emergency_type_id = et.id
            ORDER BY ep.name
            ''')
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        emergency_providers = []
        for row in rows:
            emergency_providers.append({
                'id': row[0],
                'name': row[1],
                'phone_number': row[2],
                'price': float(row[3]),
                'features': row[4],
                'map_url': row[5],
                'is_active': row[6],
                'location': row[7],
                'emergency_type': row[8]
            })
        return jsonify({'emergency_providers': emergency_providers})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#add emergency provider
@admin_bp.route('/emergency_providers', methods=['POST'])
@jwt_required()
@admin_required
def add_emergency_provider():
    data = request.get_json()
    emergency_type_id = data.get('emergency_type_id')
    name = data.get('name')
    location_id = data.get('location_id')
    phone_number = data.get('phone_number')
    price = data.get('price')
    features = data.get('features')
    map_url = data.get('map_url')
    

    if not name or not location_id or not phone_number or price is None or not emergency_type_id:
        return jsonify({'error': 'Name, location_id, phone_number, price and emergency_type_id are required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO emergency_providers (emergency_type_id,name, location_id, phone_number, price, features, map_url, is_active)
            VALUES (%s::uuid,%s, %s::uuid, %s, %s, %s, %s, %s, true)
            RETURNING id
            ''', (emergency_type_id, name, location_id, phone_number, price, features, map_url))

        emergency_provider_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Emergency provider added', 'id': emergency_provider_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#delete emergency provider
@admin_bp.route('/emergency_providers/<emergency_provider_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_emergency_provider(emergency_provider_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('DELETE FROM emergency_providers WHERE id = %s::uuid', (emergency_provider_id,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Emergency provider deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#service requests
@admin_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_service_requests():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            '''
            SELECT 
             sr.id,
                sr.status,
                sr.requested_at,
                sr.completed_at,
                u.full_name AS client_name,
                u.phone_number AS client_phone,
                l.name AS location,
                s.name AS service,
                m.full_name AS mechanic_name
            FROM service_requests sr
            JOIN users u ON sr.user_id = u.id
            JOIN locations l ON sr.location_id = l.id
            JOIN services s ON sr.service_id = s.id
            LEFT JOIN users m ON sr.mechanic_id = m.id
            ORDER BY sr.requested_at DESC
            ''')
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        requests_list = []
        for row in rows:
            requests_list.append({
                'id': row[0],
                'status': row[1],
                'requested_at': row[2],
                'completed_at': row[3],
                'client_name': row[4],
                'client_phone': row[5],
                'location': row[6],
                'service': row[7],
                'mechanic_name': row[8]
            })
        return jsonify({'requests': requests_list}),200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#delete service request
@admin_bp.route('/requests/<request_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_service_request(request_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('DELETE FROM service_requests WHERE id = %s::uuid', (request_id,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Service request deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500