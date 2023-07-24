
from flask import Blueprint, current_app,request,jsonify,json

from Middlewares.authenticator import auth_middleware

import datetime as dt
from bson import ObjectId
from bson.errors import InvalidId


from Models.booking_model import Booking


# CREATE BOOKINGS
bookings_bp = Blueprint('bookings', __name__, url_prefix = '/bookings')

@bookings_bp.route('/create', methods=['POST'])
@auth_middleware
def create_booking():
   db = current_app.db
   data = request.get_json()
   user_id = request.user_id

   # Validate that all required fields are present in the request data
   required_fields = ['property_id', 'no_of_people', 'total_fare', 'checkin_date']
   for field in required_fields:
      if field not in data:
         return jsonify({'msg': f'Missing {field} field'}), 400

   # Create a new Booking instance
   booking = Booking(
      user_id=user_id,
      property_id=data['property_id'],
      no_of_people=data['no_of_people'],
      total_fare=data['total_fare'],
      checkin_date=data['checkin_date']
   )

   # Convert the Booking instance to a dictionary
   booking_data = booking.to_document()

   # Insert the booking data into the 'bookings' collection
   db['bookings'].insert_one(booking_data)

   # Convert the ObjectId to a string before returning the response
   booking_data['_id'] = str(booking_data['_id'])

   return jsonify({'msg': 'Booking created successfully', 'booking': booking_data}),200



# DELETE BOOKINGS ONCE IT IS ATTENDED

@bookings_bp.route('/delete/<string:booking_id>', methods=['DELETE'])
@auth_middleware
def delete_booking(booking_id):
   db = current_app.db
   user_id = request.user_id

   # Check if the booking exists and get the associated property_id
   booking = db['bookings'].find_one({'_id': ObjectId(booking_id)})
   if not booking:
      return jsonify({'msg': 'Booking not found'}), 404

   # Get the property_id associated with the booking
   property_id = booking['property_id']

   # Check if the authenticated user is the host of the property associated with the booking
   property_host = db['properties'].find_one({'_id': ObjectId(property_id), 'user_id': user_id})
   if not property_host:
      return jsonify({'msg': 'Unauthorized: You are not the host of the property'}), 401

   # Check if the booking has already been attended
   if booking.get('attended', False):
      return jsonify({'msg': 'Cannot delete an un-attended booking'}), 400

   # Delete the booking from the 'bookings' collection
   db['bookings'].delete_one({'_id': ObjectId(booking_id)})

   return jsonify({'msg': 'Booking deleted successfully'}), 200



# get all the booked dates of a property
@bookings_bp.route('/<property_id>', methods=['GET'])
def get_bookings_by_property(property_id):
   db = current_app.db

   # Check if the property exists
   property = db['properties'].find_one({'_id': ObjectId(property_id)})
   if not property:
      return jsonify({'msg': 'Property not found'}), 404

   # Get all the bookings for the property
   bookings = db['bookings'].find({'property_id': property_id})

   # Extract the booked dates from the bookings
   booked_dates = [booking['checkin_date'] for booking in bookings]

   return jsonify({'property_id': property_id, 'booked_dates': booked_dates}), 200



# get all the bookings for a particular host

@bookings_bp.route('/host', methods=['GET'])
@auth_middleware
def get_bookings_by_host():
    db = current_app.db
    user_id = request.user_id

    # Check if the user is a host
    user = db['user'].find_one({'_id': ObjectId(user_id)})
    if not user or user.get('role') != 'host':
        return jsonify({'msg': 'Unauthorized, You are not a host'}), 401

    # Find all properties hosted by the host
    properties = db['properties'].find({'user_id': user_id})
    property_ids = [str(property['_id']) for property in properties]

    # Find all bookings for the host's properties
    bookings = db['bookings'].find({'property_id': {'$in': property_ids}})

    # Convert ObjectIds to strings and remove unnecessary fields
    formatted_bookings = []
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
        booking['user_id'] = str(booking['user_id'])
        formatted_bookings.append(booking)

    return jsonify({'bookings': formatted_bookings}), 200