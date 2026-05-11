from flask import Blueprint,request,jsonify
from config.db import get_db_connection

garages_bp = Blueprint('garages', __name__)

@garages_bp.route('/', methods=['GET'])
def get_garages():

    Location_ID = request.args.get('Location_ID')

    if not Location_ID:
        return jsonify({'error': 'Location_ID is required'}), 400

    conn = get_db_connection()
    cur = conn.cursor() 
    cur.execute('''
        SELECT 
            g.id,
            g.name,
            g.phone_number,
            g.address,
            g.maps_url,
            l.name AS location
        FROM garages g
        JOIN locations l ON g.location_id = l.id
        WHERE g.location_id = %s::uuid
        AND g.is_active = TRUE
        ORDER BY g.name
    ''', (Location_ID,))

    rows= cur.fetchall()
    cur.close()
    conn.close()
     
    garages = []
    for row in rows:
        garages.append({
            'id': row[0],
            'name': row[1],
            'phone_number': row[2],
            'address': row[3],
            'maps_url': row[4],
            'location': row[5]
        })
        return jsonify(garages), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500      

@garages_bp.route('/<garage_id>/services', methods=['GET'])
def get_garage_services(garage_id):
  try:
    conn = get_db_connection()
    cur = conn.cursor() 
    cur.execute('''
        SELECT 
            s.name,
            gs.price
        FROM garage_services gs
        JOIN services s ON gs.service_id = s.id
        WHERE gs.garage_id = %s::uuid
        ORDER BY s.name
    ''', (garage_id,))

    rows= cur.fetchall()
    cur.close()
    conn.close()
     
    services = []
    for row in rows:
        services.append({
            'service': row[0],
            'price': float(row[1])
        })
    return jsonify(services), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
