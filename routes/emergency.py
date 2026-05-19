from flask import Blueprint, jsonify, request
from config.db import get_db_connection

emergency_bp = Blueprint('emergency', __name__)

# GET all the three emergency types - accident/breakdown/Battery Dead/Outoffuel

@emergency_bp.route('/types', methods=['GET'])
def get_emergency_types():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, name FROM emergency_types ORDER BY name')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        types = []
        for row in rows:
            types.append({
                'id': row[0],
                'name': row[1]
                })
        return jsonify(types), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500 

# GET emergency providers by type and location (called when user picks an e.type & clicking get help)               

@emergency_bp.route('/providers',methods=['GET'])
def get_emergency_providers():
    emergency_type_id = request.args.get('type_id')
    location_id = request.args.get('location_id')
    
    # Both are required
    if not emergency_type_id:
        return jsonify({'error': 'type_id is required'}), 400
    
    if not location_id:
        return jsonify({'error': 'location_id is required'}), 400
    
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT
                ep.id,
                ep.name,
                ep.phone_number,
                ep.price,
                ep.features,
                ep.map_url,
                l.name AS location,
                et.name AS emergency_type
            FROM emergency_providers ep
            JOIN locations l ON ep.location_id = l.id
            JOIN emergency_types et ON ep.emergency_type_id = et.id
            WHERE ep.emergency_type_id = %s::uuid
            AND ep.location_id = %s::uuid
            AND ep.is_active = true
            ORDER BY ep.name
        ''', (emergency_type_id, location_id))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        providers = []
        for row in rows:
            providers.append({
                'id': row[0],
                'name': row[1],
                'phone_number': row[2],
                'price': str(row[3]) if row[3] else 'call for price',
                'features': row[4],
                'map_url': row[5],
                'location': row[6],
                'emergency_type': row[7]
            })
            
        return jsonify(providers), 200
    
    except Exception as e:       
        return jsonify({'error': str(e)}), 500