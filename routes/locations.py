from flask import Blueprint, jsonify
from config.db import get_db_connection

locations_bp = Blueprint('locations', __name__)

@locations_bp.route('', methods=['GET'])
def get_locations():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT id, name FROM locations ORDER BY name')
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        #turn each row to dict
        locations = []
        for row in rows:
            locations.append({
                'id':row[0],
                'name':row[1]
            })
            
        return jsonify(locations), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500