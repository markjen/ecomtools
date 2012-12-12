import uuid

from google.appengine.ext import ndb


class Registration(ndb.Model):
  email = ndb.StringProperty()

  @staticmethod
  def create(email):
    @ndb.transactional
    def txn(id):
      entity = Registration.get_by_id(id)
      if entity:
        return False
      entity = Registration(id=id, email=email)
      entity.put()
      return entity

    while True:
      entity = txn(uuid.uuid4().hex)
      if entity:
        return entity
