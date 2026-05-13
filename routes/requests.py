from flask import Blueprint, json, jsonify, request
from config.db import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity

requests_bp = Blueprint('requests', __name__)


# Called when a driver submits a request for a mechanic
@requests_bp.route('', methods=['POST'])
@jwt_required()
def create_request():
    identity = json.loads(get_jwt_identity())
    user_id = identity['id']
    role = identity['role']

    if role != 'user':
        return jsonify({'error': 'Only drivers can create requests'}), 403

    data = request.get_json()
    service_id = data.get('service_id')
    location_id = data.get('location_id')

    if not service_id or not location_id:
        return jsonify({'error': 'service_id and location_id are required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO service_requests (user_id, service_id, location_id, status)
            VALUES (%s::uuid, %s::uuid, %s::uuid, 'pending')
            RETURNING id
        ''', (user_id, service_id, location_id))

        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Request sent!', 'id': str(new_id)}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Called when mechanic is active and wants to see incoming requests
@requests_bp.route('', methods=['GET'])
@jwt_required()
def get_requests():
    identity = json.loads(get_jwt_identity())
    role = identity['role']

    if role != 'mechanic':
        return jsonify({'error': 'Only mechanics can view requests'}), 403

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            SELECT
                sr.id,
                sr.status,
                sr.requested_at,
                u.full_name AS client_name,
                u.phone_number AS client_phone,
                l.name AS location,
                s.name AS service
            FROM service_requests sr
            JOIN users u ON sr.user_id = u.id
            JOIN locations l ON sr.location_id = l.id
            JOIN services s ON sr.service_id = s.id
            WHERE sr.status = 'pending'
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
                'requested_at': row[2].isoformat(),
                'client_name': row[3],
                'client_phone': row[4],
                'location': row[5],
                'service': row[6]
            })

        return jsonify({'requests': requests_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# The on/off button on the mechanic dashboard
# This must be ABOVE /<request_id> so Flask does not confuse 'mechanic' as a uuid
@requests_bp.route('/mechanic/toggle', methods=['PATCH'])
@jwt_required()
def toggle_active():
    identity = json.loads(get_jwt_identity())
    user_id = identity['id']
    role = identity['role']

    if role != 'mechanic':
        return jsonify({'error': 'Only mechanics can toggle active status'}), 403

    data = request.get_json()
    is_active = data.get('is_active')

    if is_active is None:
        return jsonify({'error': 'is_active is required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            UPDATE mechanic_profiles
            SET is_active = %s
            WHERE user_id = %s::uuid
        ''', (is_active, user_id))

        conn.commit()
        cur.close()
        conn.close()

        status = 'online' if is_active else 'offline'
        return jsonify({'message': 'Active status updated successfully', 'status': status}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Called when mechanic clicks Accept or Decline on a request card
@requests_bp.route('/<request_id>', methods=['PATCH'])
@jwt_required()
def respond_to_request(request_id):
    identity = json.loads(get_jwt_identity())
    user_id = identity['id']
    role = identity['role']

    if role != 'mechanic':
        return jsonify({'error': 'Only mechanics can respond to requests'}), 403

    data = request.get_json()
    status = data.get('status')

    if status not in ['accepted', 'declined']:
        return jsonify({'error': 'Status must be accepted or declined'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT id FROM mechanic_profiles
            WHERE user_id = %s::uuid
        ''', (user_id,))
        
        result = cur.fetchone()
        if not result:
            return jsonify({'error': 'Mechanic profile not found'}), 404
        
        mechanic_id = result[0]
                    
        if status == 'accepted':
            cur.execute('''
                UPDATE service_requests
                SET status = %s,
                    mechanic_id = %s::uuid,
                    completed_at = NOW()
                WHERE id = %s::uuid
                AND status = 'pending'
            ''', (status, mechanic_id, request_id))
        else:
            cur.execute('''
                UPDATE service_requests
                SET status = %s,
                    completed_at = NOW()
                WHERE id = %s::uuid
                AND status = 'pending'
            ''', (status, request_id))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': f'Request {status} successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# After mechanic accepts, this returns the client details
# for the Call Client button
@requests_bp.route('/<request_id>', methods=['GET'])
@jwt_required()
def get_single_request(request_id):
    identity = json.loads(get_jwt_identity())
    role = identity['role']

    if role != 'mechanic':
        return jsonify({'error': 'Only mechanics can view request details'}), 403

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            SELECT
                sr.id,
                sr.status,
                u.full_name AS client_name,
                u.phone_number AS client_phone,
                l.name AS location,
                s.name AS service,
                sr.requested_at
            FROM service_requests sr
            JOIN users u ON sr.user_id = u.id
            JOIN locations l ON sr.location_id = l.id
            JOIN services s ON sr.service_id = s.id
            WHERE sr.id = %s::uuid
        ''', (request_id,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return jsonify({'error': 'Request not found'}), 404

        return jsonify({
            'id': row[0],
            'status': row[1],
            'client_name': row[2],
            'client_phone': row[3],
            'location': row[4],
            'service': row[5],
            'requested_at': row[6].isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500