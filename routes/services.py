from flask import Blueprint, jsonify
from config.db import get_db_connection

services_bp = Blueprint('services', __name__)

@services_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT id, name FROM service_categories ORDER BY name')
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        categories = []
        for row in rows:
            categories.append({
                'id':row[0],
                'name':row[1]
            })
        
        return jsonify(categories), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#Get services under a category 
#for oil service, brake inspection etc
@services_bp.route('/category/<category_id>', methods=['GET'])
def get_services_by_category(category_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT id, name
            FROM services
            WHERE category_id = %s::uuid
            ORDER BY name
            ''', (category_id,))
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        services = []
        for row in rows:
            services.append({
                'id': row[0],
                'name': row[1]
            })
        
        return jsonify(services), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500