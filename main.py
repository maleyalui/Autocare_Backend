from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from config.db import get_db_connection
from routes.auth import auth_bp
from routes.services import services_bp
from routes.locations import locations_bp
from routes.emergency import emergency_bp
from routes.admin import admin_bp
from routes.requests import requests_bp
from routes.garages import garages_bp
from routes.carwash import carwashes_bp
from routes.diagnostics import diagnostics_bp

load_dotenv()

app = Flask(__name__)

# Config
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
#needs to log in again after two days
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=2)

# Extensions
CORS(app)
jwt = JWTManager(app)

#For auth routes
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(locations_bp, url_prefix='/locations')
app.register_blueprint(services_bp, url_prefix='/services')
app.register_blueprint(emergency_bp, url_prefix='/emergency')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(requests_bp, url_prefix='/requests')
app.register_blueprint(garages_bp, url_prefix='/garages')
app.register_blueprint(carwashes_bp, url_prefix='/carwashes')
app.register_blueprint(diagnostics_bp, url_prefix='/diagnostics')

# Test route
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to Autocare!'})

# test db connection & values
@app.route('/testdb')
def test():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM locations')
        locations = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({'locations': [row[1] for row in locations]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)