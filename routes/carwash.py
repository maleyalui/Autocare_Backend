
from flask import Blueprint, jsonify, request
from config.db import get_db_connection

carwashes_bp = Blueprint('carwashes', __name__)


# GET car washes by location — shown under Car Detailing
@carwashes_bp.route('', methods=['GET'])
def get_carwashes():
    location_id = request.args.get('location_id')

    if not location_id:
        return jsonify({'error': 'location_id is required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            SELECT
                cw.id,
                cw.name,
                cw.phone_number,
                cw.price,
                cw.is_door_to_door,
                cw.features,
                cw.map_url,
                l.name AS location
            FROM car_washes cw
            JOIN locations l ON cw.location_id = l.id
            WHERE cw.location_id = %s::uuid
            AND cw.is_active = true
            ORDER BY cw.name
        ''', (location_id,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        carwashes = []
        for row in rows:
            carwashes.append({
                'id': row[0],
                'name': row[1],
                'phone_number': row[2],
                'price': str(row[3]),
                'is_door_to_door': row[4],
                'features': row[5],
                'map_url': row[6],
                'location': row[7]
            })

        return jsonify(carwashes), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500