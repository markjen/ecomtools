#!/usr/bin/env python
# To parse city_rates.csv from http://www.boe.ca.gov/sutax/pam71.htm
import argparse
import pprint

parser = argparse.ArgumentParser(description='Parse city_rates.csv from CA BoE')
parser.add_argument('-i', '--input', help='Input filename (Default: city_rates.csv)', default='city_rates.csv')
parser.add_argument('-o', '--output', help='Output filename (Default: ca.py)', default='ca.py')
args = parser.parse_args()

lines = []
with open(args.input) as input:
  lines = input.readlines()

# Rip off header lines
while not lines.pop(0).startswith('City'):
  pass

rates = []
for line in lines:
  city, rate, county = line.split(',')[:3]
  city = ' '.join([word for word in city.split(' ') if not word.startswith('(') and not word.endswith(')')])
  if city.endswith('*'):
    city = city[:-1]
  rate = float(rate[:-1])
  rates.append((city, rate, county))

with open(args.output, 'w') as output:
  output.write('RATES={}\n'.format(pprint.pformat(rates)))
