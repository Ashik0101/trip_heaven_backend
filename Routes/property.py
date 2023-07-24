
from flask import Blueprint, current_app,request,jsonify,json

from Middlewares.authenticator import auth_middleware

import datetime as dt
from bson import ObjectId
from bson.errors import InvalidId


from Models.property_model import Property

property_bp = Blueprint('property', __name__, url_prefix = '/property')

@property_bp.route('/create', methods=['POST'])
@auth_middleware
def create_property():
    db = current_app.db
    data = request.get_json()
    user_id = request.user_id

    # check if the role is 'host'
    is_user_host = db.user.find_one({"_id":ObjectId(user_id)})
    print(is_user_host['role'])
    if is_user_host['role'] != 'host':
        return jsonify({'msg':'Unauthorized,You are not a host'}),401

      
    # Validate that all required fields are present in the request data
    required_fields = ['property_type', 'location', 'title', 'description', 'price_per_night', 'amenities','thumbnail_image','other_images']
    for field in required_fields:
        if field not in data:
            return jsonify({'msg': f'Missing {field} field'}), 400

    other_image_urls = data.get('other_images')
    if not other_image_urls or not isinstance(other_image_urls, list):
        return jsonify({'msg': 'Invalid other image URLs format'}), 400

    # Create a new Property instance with the image URLs as strings
    property = Property(
        user_id=user_id,
        property_type=data['property_type'],
        location=data['location'],
        title=data['title'],
        description=data['description'],
        price_per_night=data['price_per_night'],
        amenities=data['amenities'],
        thumbnail_image=data['thumbnail_image'],
        other_images=other_image_urls
    )

    # Convert the Property instance to a dictionary
    property_data = property.to_document()

    # Insert the property data into the 'properties' collection
    db['properties'].insert_one(property_data)

    # Convert the ObjectId to a string before returning the response
    property_data['_id'] = str(property_data['_id'])

    return jsonify({'msg': 'Property created successfully', 'property': property_data})





# Get all properties created by a user
@property_bp.route('/user_properties', methods=['GET'])
@auth_middleware
def get_user_properties():
    db = current_app.db
    user_id = request.user_id
   
    # check if the role is 'host'
    is_user_host = db.user.find_one({"_id":ObjectId(user_id)})
    print(is_user_host['role'])
    if is_user_host['role'] != 'host':
        return jsonify({'msg':'Unauthorized,You are not a host'}),401

    # Find all properties created by the user with the given user_id
    properties = list(db.properties.find({'user_id': user_id}))
    
    # Convert the ObjectId to a string for serialization in the response
    for property in properties:
        property['_id'] = str(property['_id'])

    return jsonify({'msg': 'Success', 'properties': properties})




# Get a specific property by its ID
@property_bp.route('/<property_id>', methods=['GET'])
def get_property_by_id(property_id):
    db = current_app.db

    try:
        # Convert the property_id to ObjectId
        property_id = ObjectId(property_id)
    except InvalidId:
        return jsonify({'msg': 'Invalid property ID'}), 400

    # Find the property with the given property_id
    property = db.properties.find_one({'_id': property_id})

    if not property:
        return jsonify({'msg': 'Property not found'}), 404

    # Convert the ObjectId to a string for serialization in the response
    property['_id'] = str(property['_id'])

    return jsonify({'msg': 'Success', 'property': property})



# Get all properties without authentication
@property_bp.route('/', methods=['GET'])
def get_all_properties():
    db = current_app.db

    # Find all properties in the 'properties' collection
    properties = list(db.properties.find())

    # Convert the ObjectId to a string for serialization in the response
    for property in properties:
        property['_id'] = str(property['_id'])

    return jsonify({'msg': 'Success', 'properties': properties})
@property_bp.after_request
def add_cache_control(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


# Delete a property by it's id
@property_bp.route('/delete/<property_id>', methods=['DELETE'])
@auth_middleware
def delete_property(property_id):
    db = current_app.db
    user_id = request.user_id

    try:
        # Convert the property_id to ObjectId
        property_id = ObjectId(property_id)
    except InvalidId:
        return jsonify({'msg': 'Invalid property ID'}), 400

    # check if the role is 'host'
    is_user_host = db.user.find_one({"_id":ObjectId(user_id)})
    print(is_user_host['role'])
    if is_user_host['role'] != 'host':
        return jsonify({'msg':'Unauthorized,You are not a host'}),401

    # Find the property by its ID and the user's ID
    property_to_delete = db.properties.find_one({'_id':ObjectId(property_id)})
    if not property_to_delete:
        return jsonify({'msg': 'Property not found'}), 404
    if property_to_delete['user_id'] != user_id:
        return jsonify({'msg':'You are not authorized to delete this property'}),401
    property_to_delete = db.properties.find_one({'_id': ObjectId(property_id), 'user_id': user_id})

    # Delete the property from the 'properties' collection
    db.properties.delete_one({'_id': ObjectId(property_id)})

    return jsonify({'msg': 'Property deleted successfully'}), 200



# Update property details
@property_bp.route('/update_property/<property_id>', methods=['PUT'])
@auth_middleware
def update_property(property_id):
    db = current_app.db
    user_id = request.user_id  # Extract user ID from the request or JWT payload
    data = request.get_json()

    # Check if the user is host
    is_user_host = db.user.find_one({"_id": ObjectId(user_id)})
    if is_user_host['role'] != 'host':
        return jsonify({'msg': 'Unauthorized, You are not a host'}), 401

    # Find the property by its ID
    property = db.properties.find_one({'_id': ObjectId(property_id)})
    if not property:
        return jsonify({'msg': 'Property not found'}), 404

    # Check if the user is the owner of the property
    if property['user_id'] != user_id:
        return jsonify({'msg': 'You are not authorized to update this property'}), 401

    # Update the property data fields using $set operator
    update_fields = {}
    for key, value in data.items():
        update_fields[f'{key}'] = value

    db.properties.update_one(
        {'_id': ObjectId(property_id)},
        {'$set': update_fields}
    )

    # Fetch and return the updated property
    updated_property = db.properties.find_one({'_id': ObjectId(property_id)})

    # Convert the ObjectId to a string for serialization
    updated_property['_id'] = str(updated_property['_id'])

    return jsonify({'msg': 'Property updated successfully', 'property': updated_property})




# Add images into other_images list
@property_bp.route('/add_images/<property_id>', methods=['POST'])
@auth_middleware
def add_images(property_id):
    db = current_app.db
    user_id = request.user_id  # Extract user ID from the request or JWT payload

    # Check if the user is host
    is_user_host = db.user.find_one({"_id": ObjectId(user_id)})
    if is_user_host['role'] != 'host':
        return jsonify({'msg': 'Unauthorized, You are not a host'}), 401

    # Find the property by its ID
    property = db.properties.find_one({'_id': ObjectId(property_id)})
    if not property:
        return jsonify({'msg': 'Property not found'}), 404

    # Check if the user is the owner of the property
    if property['user_id'] != user_id:
        return jsonify({'msg': 'You are not authorized to add images to this property'}), 401

    # Get the list of existing other_images or initialize it as an empty list
    other_images = property.get('other_images', [])

    data = request.get_json()
    new_images = data.get('images')

    if not new_images or not isinstance(new_images, list):
        return jsonify({'msg': 'Invalid image URLs format'}), 400

    # Add the new images to the existing other_images list
    other_images.extend(new_images)

    # Update the property data with the new other_images list
    db.properties.update_one(
        {'_id': ObjectId(property_id)},
        {'$set': {'other_images': other_images}}
    )

    # Fetch and return the updated property
    updated_property = db.properties.find_one({'_id': ObjectId(property_id)})

    # Convert the ObjectId to a string for serialization
    updated_property['_id'] = str(updated_property['_id'])

    return jsonify({'msg': 'Images added successfully', 'property': updated_property})
