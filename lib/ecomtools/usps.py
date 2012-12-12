import logging
import string
import urllib
from xml.dom import minidom


user_id = ''
test = False


def get_urlbase(secure):
  if test:
    if secure:
      return 'https://secure.shippingapis.com/ShippingAPITest.dll'
    else:
      return 'http://testing.shippingapis.com/ShippingAPITest.dll'
  else:
    if secure:
      return 'https://secure.shippingapis.com/ShippingAPI.dll'
    else:
      return 'http://production.shippingapis.com/ShippingAPI.dll'


template_strings = {
  'Verify':'''
<AddressValidateRequest USERID="$userid">
  <Address ID="0">
    <FirmName>$firmname</FirmName>
    <Address1>$address1</Address1>
    <Address2>$address2</Address2>
    <City>$city</City>
    <State>$state</State>
    <Zip5>$zip5</Zip5>
    <Zip4>$zip4</Zip4>
  </Address>
</AddressValidateRequest>
''',
  'TrackV2': '''
<TrackFieldRequest USERID="$userid">
  <TrackID ID="$id"></TrackID>
</TrackFieldRequest>
'''
}
templates = {}
for name, template_string in template_strings.iteritems():
  templates[name] = string.Template(''.join([line.strip()
                                             for line in template_string.split('\n') if line]))


def extract_text(dom, tagName):
  nodes = dom.getElementsByTagName(tagName)
  if nodes:
    node = nodes[0]
    return ''.join([child.data for child in node.childNodes if child.nodeType == child.TEXT_NODE])
  return None


def extract(dom, fields):
  return {field: extract_text(dom, field) for field in fields}


def make_request(api, values, secure=True):
  xml = templates[api].substitute(values)
  url = '{}?{}'.format(get_urlbase(secure), urllib.urlencode([('API', api),('XML', xml)]))
  logging.debug(url)
  response = urllib.urlopen(url).read()
  logging.debug(response)
  return minidom.parseString(response)


def verify(**kwargs):
  values = {
    'userid': user_id,
    'firmname': '',
    'address1': '',
    'address2': '',
    'city': '',
    'state': '',
    'zip5': '',
    'zip4': '',
  }
  values.update(kwargs)
  logging.debug('Making Verify request with params {}'.format(values))
  dom = make_request('Verify', values)
  error = dom.getElementsByTagName('Error')
  if error:
    return extract(dom, ['Number', 'Description', 'Source'])
  return extract(dom, ['Address1', 'Address2', 'FirmName', 'City', 'State', 'Zip5', 'Zip4'])


def track(id):
  values = {
    'userid': user_id,
    'id': id
  }
  logging.debug('Making TrackV2 request with params {}'.format(values))
  dom = make_request('TrackV2', values, secure=False)
  error = dom.getElementsByTagName('Error')
  if error:
    return extract(dom, ['Number', 'Description', 'Source'])

  def extract_event(element):
    return extract(element, ['Event', 'EventDate', 'EventTime', 'EventCity', 'EventZIPCode', 'EventState'])
  return {node_name: [extract_event(element) for element in dom.getElementsByTagName(node_name)] for node_name in ['TrackSummary', 'TrackDetail']}


