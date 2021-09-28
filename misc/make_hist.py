#!/usr/bin/env python3

import sys
import re
import csv
import json

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield row

if len(sys.argv) != 3:
    print("Usage make_hist.py <metadata csv file> <json file>")
    sys.exit(-1)

fp = None
try:
    fp = open(sys.argv[1], "r")
except IOError:
    print("Cannot open input file %s" % sys.argv[1])
    sys.exit(0)

_out = None
try:
    _out = open(sys.argv[2], "w")
except IOError:
    print("Cannot open output file %s" % sys.argv[2])
    sys.exit(0)

out = csv.writer(_out, quoting=csv.QUOTE_MINIMAL)

ages = {}
countries = {}
ethnicities = {}

lines = []
reader = unicode_csv_reader(fp)
for i, line in enumerate(reader):
    if not i:
        continue

    temp_id = line[0]
    code = line[1]
    age = int(line[2])
    country = line[3]
    ethnicity = line[4].lower()

    if ethnicity in ('-', ''):
        ethnicity = "(declined to state)"
    if country in ('-', ''):
        country = "(unknown)"

    if age:
        try:
            ages[age] += 1
        except KeyError:
            ages[age] = 1

    if country != 'XX':
        try:
            countries[country] += 1
        except KeyError:
            countries[country] = 1

    if ethnicity != '':
        try:
            ethnicities[ethnicity] += 1
        except KeyError:
            ethnicities[ethnicity] = 1

data = {
    'ages' : ages,
    'countries' : countries,
    'ethnicities' : ethnicities
}

_out.write(json.dumps(data, indent=4, sort_keys=True))

fp.close()
_out.close()
