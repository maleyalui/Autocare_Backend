
from flask import Blueprint, jsonify, request
from config.db import get_db_connection

diagnostics_bp = Blueprint('diagnostics', __name__)


# GET diagnostic centers by location — shown under Diagnostics
@diagnostics_bp.route('', methods=['GET'])
def get_diagnostics():
    location_id = request.args.get('location_id')

    if not location_id:
        return jsonify({'error': 'location_id is required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            SELECT
                dc.id,
                dc.name,
                dc.phone_number,
                dc.price_from,
                dc.features,
                dc.map_url,
                l.name AS location
            FROM diagnostics_centres dc
            JOIN locations l ON dc.location_id = l.id
            WHERE dc.location_id = %s::uuid
            AND dc.is_active = true
            ORDER BY dc.name
        ''', (location_id,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        centers = []
        for row in rows:
            centers.append({
                'id': row[0],
                'name': row[1],
                'phone_number': row[2],
                'price_from': str(row[3]),
                'features': row[4],
                'map_url': row[5],
                'location': row[6]
            })

        return jsonify(centers), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500