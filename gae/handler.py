import json

from google.appengine.api import app_identity
from google.appengine.api import mail
import webapp2
from webapp2_extras import jinja2

import config
from ecomtools import usps
import model


usps.user_id = config.USPS_USER_ID


class TemplateHandler(webapp2.RequestHandler):
  content_type = 'text/html'
  template_filename = None

  def __init__(self, request, response):
    super(TemplateHandler, self).__init__(request, response)
    self.values = {}

  @webapp2.cached_property
  def jinja2(self):
    return jinja2.get_jinja2(app=self.app)

  def render_template(self):
    if not self.template_filename:
      raise Exception('No template filename')
    self.response.headers['Content-Type'] = self.content_type
    self.response.write(self.jinja2.render_template(self.template_filename, **self.values))


class IndexHandler(TemplateHandler):
  template_filename = 'index.html'
  def get(self):
    self.render_template()


class RegisterHandler(TemplateHandler):
  template_filename = 'register.html'
  def post(self):
    email = self.request.get('email')
    if email:
      email_parts = email.split('@')
      if len(email_parts) == 2:
        entity = model.Registration.create(email)
        mail.send_mail(
            sender='noreply@{}.appspotmail.com'.format(app_identity.get_application_id()),
            to=email,
            subject='eCommerce tools API key',
            body='Your API key is "{}"'.format(entity.key.id()))
        self.values['email'] = email
        self.render_template()
      else:
        self.abort(400, 'Invalid email specified ({})'.format(email))
    else:
      self.abort(400, 'No email specified')


class ApiHandler(webapp2.RequestHandler):
  def verify_api_key(self):
    key = self.request.get('key')
    if key:
      registration = model.Registration.get_by_id(key)
      if registration:
        return
    self.abort(403, 'Invalid API key "{}"'.format(key))

  def json_out(self, value):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(value))


class UspsVerifyHandler(ApiHandler):
  def get(self):
    self.verify_api_key()
    self.json_out(usps.verify(**self.request.params.copy()))


class UspsTrackHandler(ApiHandler):
  def get(self):
    self.verify_api_key()
    id = self.request.get('id')
    if id:
      self.json_out(usps.track(self.request.get('id')))
    else:
      self.abort(400, 'No id specified')
