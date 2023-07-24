from flask import Flask, request, jsonify
from bcrypt import hashpw, gensalt

app = Flask(__name__)

class User:
    def __init__(self, name, email, password, date_of_birth, gender, bio=''):
        self.name = name
        self.email = email
        self.password = self._hash_password(password)  # Hash the password
        self.bio = bio
        self.date_of_birth = date_of_birth
        self.gender = gender

    def _hash_password(self, password):
        salt = gensalt()
        hashed_password = hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def to_document(self):
        return {
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'role': 'user',
            'bio': self.bio,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender
        }
