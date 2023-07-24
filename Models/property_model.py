from bson import ObjectId

class Property:
    def __init__(self, user_id, property_type, location, title, description, price_per_night, amenities, thumbnail_image, other_images):
        self.user_id = user_id
        self.property_type = property_type
        self.location = location
        self.title = title
        self.description = description
        self.price_per_night = price_per_night
        self.amenities = amenities
        self.thumbnail_image = thumbnail_image
        self.other_images = other_images

    def to_document(self):
        return {
            'user_id': self.user_id,
            'property_type': self.property_type,
            'location': self.location,
            'title': self.title,
            'description': self.description,
            'price_per_night': self.price_per_night,
            'amenities': self.amenities,
            'thumbnail_image': self.thumbnail_image,
            'other_images': self.other_images
        }
