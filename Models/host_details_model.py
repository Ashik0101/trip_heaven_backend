class HostDetails:
   def __init__(self, user_id, location, property_type,hosting_status, hosting_since, about):
      self.user_id = user_id
      self.location = location
      self.property_type = property_type
      self.hosting_status = hosting_status
      self.hosting_since = hosting_since
      self.about = about

   def to_document(self):
      return {
         'user_id': self.user_id,
         'location': self.location,
         'property_type': self.property_type,
         'hosting_since': self.hosting_since,
         'hosting_status':self.hosting_status,
         'about': self.about
      }
