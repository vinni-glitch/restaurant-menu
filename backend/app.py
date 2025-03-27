from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import DATABASE_URL
from models import db
from routes import menu_routes, auth_routes

# Initialize Flask app
app = Flask(__name__)

# Set the secret key for JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Change this to a secure key!
jwt = JWTManager(app)  # Initialize JWT Manager

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Enable CORS
CORS(app)

# Register API routes
app.register_blueprint(menu_routes, url_prefix='/menu')
app.register_blueprint(auth_routes, url_prefix='/auth')

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
