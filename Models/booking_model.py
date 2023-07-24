from flask import current_app
from bson.objectid import ObjectId

class Booking:
    def __init__(self, user_id, property_id, no_of_people, total_fare, checkin_date, attended=False):
        self.user_id = user_id
        self.property_id = property_id
        self.no_of_people = no_of_people
        self.total_fare = total_fare
        self.checkin_date = checkin_date
        self.attended = attended

    def to_document(self):
        return {
            'user_id': self.user_id,
            'property_id': self.property_id,
            'no_of_people': self.no_of_people,
            'total_fare': self.total_fare,
            'checkin_date': self.checkin_date,
            'attended': self.attended
        }
