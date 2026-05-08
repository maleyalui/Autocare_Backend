from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Config
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Extensions
CORS(app)
jwt = JWTManager(app)

# Test route
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to Autocare!'})

if __name__ == '__main__':
    app.run(debug=True)