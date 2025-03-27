from flask import Blueprint, jsonify, request
from models import db, MenuItem, User, Order
from utils.menu_utils import MenuRecommendation
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

menu_routes = Blueprint('menu_routes', __name__)
auth_routes = Blueprint('auth_routes', __name__)

menu_recommendation = MenuRecommendation()
CORS(menu_routes)
CORS(auth_routes)

### 🔑 USER AUTHENTICATION & AUTHORIZATION ENDPOINTS ###

@auth_routes.route('/register', methods=['POST'])
def register():
    """
    Register a new user (Admin/User).
    """
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password') or not data.get('role'):
            return jsonify({"error": "All fields are required"}), 400

        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400

        new_user = User(username=data['username'], role=data['role'])
        new_user.set_password(data['password'])  # Hash password

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@auth_routes.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and return JWT token if valid.
    """
    try:
        data = request.get_json()

        if not data or "username" not in data or "password" not in data:
            return jsonify({"error": "Invalid request format"}), 400

        user = User.query.filter_by(username=data.get('username')).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not user.check_password(data.get('password')):
            return jsonify({"error": "Invalid password"}), 401

        access_token = create_access_token(identity={"username": user.username, "role": user.role})
        return jsonify({"message": "Login successful", "token": access_token, "role": user.role}), 200

    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


### 🍽️ MENU MANAGEMENT ENDPOINTS ###

@menu_routes.route('/items', methods=['GET'])
def get_menu():
    """
    Fetch all menu items.
    """
    try:
        items = MenuItem.query.all()
        return jsonify([item.serialize() for item in items])
    except Exception as e:
        return jsonify({"error": f"Failed to fetch menu items: {str(e)}"}), 500

@menu_routes.route('/add', methods=['POST'])
@jwt_required()
def add_menu_item():
    """
    Admin-only: Add a new menu item.
    """
    try:
        current_user = get_jwt_identity()
        if current_user["role"] != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        if not data or "name" not in data or "price" not in data or "category" not in data:
            return jsonify({"error": "All fields are required"}), 400

        new_item = MenuItem(
            name=data['name'],
            price=data['price'],
            category=data['category']
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "Menu item added!"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add menu item: {str(e)}"}), 500

@menu_routes.route('/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_menu_item(item_id):
    """
    Admin-only: Update a menu item.
    """
    try:
        current_user = get_jwt_identity()
        if current_user["role"] != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request"}), 400

        item = MenuItem.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        item.name = data.get('name', item.name)
        item.price = data.get('price', item.price)
        item.category = data.get('category', item.category)

        db.session.commit()
        return jsonify({"message": "Menu item updated!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update menu item: {str(e)}"}), 500

@menu_routes.route('/delete/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_menu_item(item_id):
    """
    Admin-only: Delete a menu item.
    """
    try:
        current_user = get_jwt_identity()
        if current_user["role"] != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        item = MenuItem.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Menu item deleted!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete menu item: {str(e)}"}), 500


### 🛒 ORDER & RECOMMENDATION ENDPOINTS ###

@menu_routes.route('/order/<int:item_id>', methods=['POST'])
@jwt_required()
def place_order(item_id):
    """
    User-only: Place an order for a menu item.
    """
    current_user = get_jwt_identity()
    if current_user["role"] != "user":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    print("🛠 Received JSON Payload:", data)  # ✅ Debugging print statement

    if not data or "quantity" not in data:
        return jsonify({"error": "Missing quantity"}), 422  # ✅ Return proper error message

    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    quantity = int(data["quantity"])  # Ensure it's an integer

    new_order = Order(
        user_id=User.query.filter_by(username=current_user["username"]).first().id, 
        menu_item_id=item.id, 
        quantity=quantity
    )

    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": f"Order placed for {quantity}x {item.name}"}), 200



@menu_routes.route('/recommendations', methods=['GET'])
def get_recommendations():
    """
    Returns the top 3 most popular menu items based on order frequency.
    """
    try:
        menu_recommendation = MenuRecommendation()
        popular_items = menu_recommendation.get_popular_items()
        return jsonify({"popular_dishes": popular_items}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch recommendations: {str(e)}"}), 500
