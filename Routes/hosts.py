
from flask import Blueprint, current_app,request,jsonify,json
from Models.host_details_model import HostDetails
from Middlewares.authenticator import auth_middleware

import datetime as dt
from bson import ObjectId
from bson.errors import InvalidId


from dotenv import load_dotenv
load_dotenv()
import os


host_bp = Blueprint('host', __name__, url_prefix = '/host')


# Add host details
@host_bp.route('/add_host_details', methods=['POST'])
@auth_middleware
def add_host_details():
   db = current_app.db
   data = request.get_json()
   user_id = request.user_id  # Extract user ID from the request or JWT payload

   # Validate that all required fields are present in the request data
   required_fields = ['location', 'property_type','hosting_status', 'hosting_since', 'about']
   for field in required_fields:
      if field not in data:
         return jsonify({'msg': f'Missing {field} field'}), 400

   # Create a new HostDetails instance
   host_details = HostDetails(
      user_id=user_id,
      location=data['location'],
      property_type=data['property_type'],
      hosting_status = data['hosting_status'],
      hosting_since=data['hosting_since'],
      about=data['about']
   )

   # Convert the HostDetails instance to a dictionary
   host_details_data = host_details.to_document()

   # Insert the host details into the 'hosts' collection
   db['hosts'].insert_one(host_details_data)

   # Convert the ObjectId to a string before returning the response
   host_details_data['_id'] = str(host_details_data['_id'])

   return jsonify({'msg': 'Host details added successfully', 'host_details': host_details_data})



# Get host details
@host_bp.route('/host_details', methods=['GET'])
@auth_middleware
def get_host_details():
   user_id = request.user_id
   db = current_app.db
    # Check if the user is host
   is_user_host = db.user.find_one({"_id":ObjectId(user_id)})
   print(is_user_host['role'])
   if is_user_host['role'] != 'host':
      return jsonify({'msg':'Unauthorized,You are not a host'}),401

   # Get the host_details for the specified user_id
   host_details = db.hosts.find_one({'user_id': user_id})

   if host_details:
      # Convert the ObjectId to a string for serialization
      host_details['_id'] = str(host_details['_id'])

      # Convert hosting_since to a datetime object
      host_details['hosting_since'] = dt.datetime.strptime(host_details['hosting_since'], "%Y-%m-%d")


      # Format the hosting_since date
      host_details['hosting_since'] = dt.datetime.strftime(host_details['hosting_since'], "%B %d, %Y")
      return jsonify({'msg': 'Success', 'host_details': host_details})
   else:
      return jsonify({'msg': 'Host details not found'}), 404



# Update host details 
@host_bp.route('/update_host_details', methods=['PATCH'])
@auth_middleware
def update_host_details():
   db = current_app.db
   user_id = request.user_id  # Extract user ID from the request or JWT payload
   data = request.get_json()

   # Check if the user is host
   is_user_host = db.user.find_one({"_id":ObjectId(user_id)})
   print(is_user_host['role'])
   if is_user_host['role'] != 'host':
      return jsonify({'msg':'Unauthorized,You are not a host'}),401
   # Check if the host details exist for the user
   existing_host_details = db.hosts.find_one({'user_id': user_id})

   if not existing_host_details:
      return jsonify({'msg': 'Host details not found for this user'}), 404

   # Update the host details fields using $set operator
   update_fields = {}
   for key, value in data.items():
      update_fields[f'{key}'] = value

   db.hosts.update_one(
      {'user_id': user_id},
      {'$set': update_fields}
   )

   # Fetch and return the updated host details
   updated_host_details = db.hosts.find_one({'user_id': user_id})

   # Convert the ObjectId to a string for serialization
   updated_host_details['_id'] = str(updated_host_details['_id'])

   # Convert hosting_since to a datetime object
   updated_host_details['hosting_since'] = dt.datetime.strptime(updated_host_details['hosting_since'], "%Y-%m-%d")

   # Format the hosting_since date
   updated_host_details['hosting_since'] = dt.datetime.strftime(updated_host_details['hosting_since'], "%B %d, %Y")

   return jsonify({'msg': 'Host details updated successfully', 'host_details': updated_host_details})
