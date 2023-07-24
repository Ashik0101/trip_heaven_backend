import jwt
from functools import wraps
from flask import request, jsonify

from dotenv import load_dotenv
load_dotenv()
import os


# Authorization Middleware
def auth_middleware(f):
   @wraps(f)
   def decorated_function(*args, **kwargs):
      try:
         # Get the 'Authorization' header from the request and split the token
         authorization_header = request.headers.get('Authorization')
         if authorization_header:
               token = authorization_header.split(" ")[1]
         else:
               return jsonify({'msg': 'Missing Authorization header'}), 401

         decoded_token = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
         user_id = decoded_token['user_id']

         # Add the user's role to the request context for later use
         request.user_id = user_id

         return f(*args, **kwargs)
      except jwt.ExpiredSignatureError:
         return jsonify({'msg': 'Token has expired'}), 401
      except jwt.InvalidTokenError:
         return jsonify({'msg': 'Invalid token'}), 401
      except IndexError:
         return jsonify({'msg': 'Invalid Authorization header format'}), 401
      except Exception as e:
         return jsonify({'msg': f'Error occurred: {e}'}), 500

   return decorated_function

