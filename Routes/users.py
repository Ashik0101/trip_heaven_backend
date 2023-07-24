
from flask import Blueprint, current_app,request,jsonify,json
from Models.user_model import User
from Middlewares.authenticator import auth_middleware

from dotenv import load_dotenv
load_dotenv()
import os


from bcrypt import checkpw
import jwt
import datetime

from bson import ObjectId
from bson.errors import InvalidId

# REGISTRATION LOGIC

auth_bp = Blueprint('auth', __name__, url_prefix = '/auth')
user_bp = Blueprint('user', __name__, url_prefix = "/user")


# Authentication routes here......
@auth_bp.route('/register', methods=['POST'])
def register():
    # Access the database using current_app
    db = current_app.db
    data = request.get_json()
    if 'name' not in data or 'email' not in data or 'password' not in data or 'date_of_birth' not in data or 'gender' not in data:
        return jsonify({'msg':'Please provide all the fields'}),400

    if data['gender'].lower() not in ['male','female','other']:
        return jsonify({'msg':'Invalid gender'}),400

    # Check if the user with the given email already exists
    existing_user = db.user.find_one({'email': data['email']})
    if existing_user:
        return jsonify({'msg': 'User already registered with this email'}), 409

    # Create a new User instance
    user = User( data['name'], data['email'],data['password'], data['date_of_birth'], data['gender'],data.get('bio', ''))

    # Convert the User instance to a dictionary
    user_data = user.to_document()

    # Insert the user_data into the 'user' collection
    db['user'].insert_one(user_data)

    # convert object id to str
    user_data['_id'] = str(user_data['_id'])

    # Remove the 'password' field from the user_data dictionary before returning it as JSON
    user_data.pop('password', None)
    return jsonify({'msg':'User registered successfully','user_data':user_data}),201
   

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><> #
    
# LOGIN LOGIC

@auth_bp.route('/login', methods=['POST'])
def login():
    # Access the database using current_app
    db = current_app.db
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return jsonify({'msg':'Please provide all the fields'}),400

    # Check if the user with this mail exists
    existing_user = db.user.find_one({'email': data['email']})
    if not existing_user:
        return jsonify({'msg': 'User not found, please register first'}), 404

    
    # Compare the provided password with the hashed password stored in the database
    if checkpw(data['password'].encode('utf-8'), existing_user['password'].encode('utf-8')):
        # Passwords match, create a JWT token
        token_payload = {
            'user_id': str(existing_user['_id']),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # Token will expire in  7 days 
        }
    
        secret_key =  os.getenv('SECRET_KEY') # Replace with your secret key for JWT
        token = jwt.encode(token_payload, secret_key, algorithm='HS256')

        # Return the success response along with the token
        return jsonify({'msg': 'Login successful', 'token': token}), 200
    else:
        # Passwords don't match, return error response
        return jsonify({'msg': 'Invalid password'}), 400
   


# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><> #


# User managment routes are here...

# Get a user by it's id.

@user_bp.route('/profile', methods=['GET'])
@auth_middleware
def get_user():
    user_id = request.user_id  # Extract user ID from the request or JWT payload
    print(user_id)
    # Access the database using current_app
    db = current_app.db

    # Check if the user with the given ID exists
    existing_user = db.user.find_one({'_id': ObjectId(user_id)})
    if not existing_user:
        return jsonify({'msg': 'User not found'}), 404

    # Convert the MongoDB ObjectId to a string
    existing_user['_id'] = str(existing_user['_id'])

    existing_user['date_of_birth'] = datetime.datetime.strptime(existing_user['date_of_birth'], "%Y-%m-%d")

    # Format the hosting_since date
    existing_user['date_of_birth'] = datetime.datetime.strftime(existing_user['date_of_birth'], "%B %d, %Y")
    # Remove the 'password' field from the user data before returning it as JSON
    existing_user.pop('password', None)

    return jsonify(existing_user)



# Update user details route
@user_bp.route('/update/<user_id>', methods=['PUT'])
def update_user(user_id):
    # Access the database using current_app
    db = current_app.db
    data = request.get_json()

    # Fetch the user data from the database
    existing_user = db.user.find_one({'_id': ObjectId(user_id)})
    if not existing_user:
        return jsonify({'msg': 'User not found'}), 404

    # Update user details based on the data from the request
    existing_user['name'] = data.get('name', existing_user['name'])
    existing_user['email'] = data.get('email', existing_user['email'])
    existing_user['gender'] = data.get('gender', existing_user['gender'])
    existing_user['date_of_birth'] = data.get('date_of_birth', existing_user['date_of_birth'])
    existing_user['bio'] = data.get('bio', existing_user['bio'])

    # Update the user data in the database
    db.user.update_one({'_id': ObjectId(user_id)}, {'$set': existing_user})

    # Remove the 'password' field from the user data before returning it as JSON
    existing_user.pop('password', None)

    # Convert the MongoDB ObjectId to a string
    existing_user['_id'] = str(existing_user['_id'])
    return jsonify({'msg': 'User details updated successfully', 'user_data': existing_user}),200



# UPdate role from 'user' to 'host'
# Example route that requires authorization based on user role
@user_bp.route('/update_role_to_host', methods=['PUT'])
@auth_middleware
def update_user_role():
    user_id = request.user_id  # Extract user ID from the request or JWT payload
    db = current_app.db
    # Update the user data in the database
    db.user.update_one({'_id': ObjectId(user_id)}, {'$set': {'role':'host'}})

   # Fetch the updated user data from the database
    updated_user = db.user.find_one({'_id': ObjectId(user_id)}, {'password': 0})  # Excluding 'password' field
    # Convert the ObjectId to string for the 'id' field
    updated_user['_id'] = str(updated_user['_id'])
    print(updated_user)

    return jsonify({'msg': 'Success','user_data':updated_user})

