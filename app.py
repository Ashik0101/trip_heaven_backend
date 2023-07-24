from flask import Flask, request, jsonify,Response
from flask_cors import CORS
from pymongo import MongoClient
from bson import json_util
from bson import ObjectId
from bson.errors import InvalidId
import json

from dotenv import load_dotenv
load_dotenv()
import os



from Routes.users import auth_bp
from Routes.users import user_bp
from Routes.hosts import host_bp
from Routes.property import property_bp
from Routes.bookings import bookings_bp
# Create the Flask app
    # app = Flask(__name__)
    # CORS(app)
    # client = MongoClient(os.getenv('MONGO_URI'))
    # db = client['trip_heaven']
    # collection = db['user']
def create_app():
    app = Flask(__name__)
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.mongo_client = MongoClient(app.config['MONGO_URI'])
    app.db = app.mongo_client['trip_heaven']
    collection = app.db['user']

    # Add CORS middleware to allow cross-origin requests
    CORS(app)

    # check if mongoDB connected
    try:
        # Access a collection to check the connection
        count = collection.count_documents({})
        print(f"MongoDB connected. Collection count: {count}")
    except ConnectionError as e:
        print(f"Failed to connect to MongoDB. Error: {str(e)}")


    
    # Register the blueprints with the app
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(host_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(bookings_bp)
    return app
    
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
    



