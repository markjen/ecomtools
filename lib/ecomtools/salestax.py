import json
import logging
import urllib

from rates import ca


def normalize_name(name):
  return ''.join(name.split(' ')).lower().replace("'", '')


CA = {}
for city, rate, county in ca.RATES:
  normalized_city = normalize_name(city)
  if normalized_city not in CA:
    CA[normalized_city] = {}
  CA[normalized_city][normalize_name(county)] = rate


def lookup(city, state, zip5, estimate=True):
  if state.upper() == 'CA':
    city_rates = CA.get(normalize_name(city))
    if city_rates:
      if len(city_rates) == 1:
        return city_rates.values()[0]
      logging.info('More than one rate found for %s, %s. Attempting geocode...', city, state)
    else:
      logging.info('No rates found for %s, %s. Attempting geocode...', city, state)
    # pull city, county from zip code
    geocode_url = 'http://maps.googleapis.com/maps/api/geocode/json?{}'.format(urllib.urlencode([('sensor', 'false'), ('address', zip5)]))
    try:
      geodata = json.loads(urllib.urlopen(geocode_url).read())
    except Exception, e:
      logging.exception(e)
    else:
      results = geodata.get('results')
      if results:
        result = results[0]
        city_name = None
        county_name = None
        for component in result.get('address_components'):
          if 'administrative_area_level_2' in component.get('types'):
            county_name = component.get('long_name')
          if 'locality' in component.get('types'):
            city_name = component.get('long_name')
        if city_name:
          city_rates = CA.get(normalize_name(city_name))
          if city_rates:
            if len(city_rates) == 1:
              return city_rates.values()[0]
            if county_name:
              rate = city_rates.get(normalize_name(county_name))
              if rate:
                return rate
            logging.warning('Multiple city rates found for geocoded zip %s (%s) no county match %s', zip5, city_rates, county_name)
          else:
            logging.warning('No city rates found for geocoded zip %s', zip5)
        else:
          logging.warning('No city name found for geocoded zip %s', zip5)
    logging.warning('Tax rate for %s, %s %s not found', city, state, zip5)
    if estimate:
      return 7.25
  return None
