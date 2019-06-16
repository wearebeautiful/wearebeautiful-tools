#!/usr/bin/env python

import json
import click
import sys
import datetime

FORMAT_VERSION = 1 
ALLOWED_KEYS = [ "version", "id", "created", "gender", "gender_comment", "country", "age", "body_type", 
    "mother", "ethnicity", "modification", "comment", "other"]
GENDERS = ["female", "male", "trans-mtf", "trans-ftm", "other"]
COUNTRIES = [ "AF", "AL", "DZ", "Sa", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY",
"BE", "BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR", "IO", "BN", "BG", "BF", "BI", "CV", "KH", "CM", "CA",
"KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO", "KM", "CD", "CG", "CK", "CR", "HR", "CU", "CW", "CY", "CZ", "CI", "DK",
"DJ", "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "SZ", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA",
"GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "-B", "GY", "HT", "HM", "VA", "HN", "HK",
"HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW",
"KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ",
"MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "NC", "NZ", "NI",
"NE", "NG", "NU", "NF", "MP", "NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA",
"RO", "RU", "RW", "RE", "BL", "a ", "KN", "LC", "MF", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG",
"SX", "SK", "SI", "SB", "SO", "ZA", "GS", "SS", "ES", "LK", "SD", "SR", "SJ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH",
"TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "UM", "US", "UY", "UZ", "VU", "VE",
"VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW", "AX" ]
BODY_TYPES = ["thin", "fit", "full", "overweight"]
MIN_ETHNICITY_LEN = 5
MODIFICATIONS = ["none", "circumcised"," fgm", "labiaplasty", "masectomy", "female-to-male","male-to-female"]

def validate_manifest(manifest):
    
    if manifest['version'] != FORMAT_VERSION:
        print("Incorrect format version. This script can only accept version %s" % FORMAT_VERSION)
        sys.exit(-1)

    if sorted(manifest.keys()) != sorted(ALLOWED_KEYS):
        print("incorrect top level fields. Got\n%s\n\Allowed:\n%s" % (sorted(manifest.keys), sorted(ALLOWED_KEYS)))
        sys.exit(-1)

    if len(manifest['id']) != 4:
        print("Incorrect ID length")
        sys.exit(-1)

    try:
        id = int(manifest['id'])
    except ValueError:
        print("Incorrect ID format. Must be a 4 digit number.")
        sys.exit(-1)

    year, month = manifest['created'].split('-')
    if len(year) != 4 and len(month) != 2:
        print("Created field should be of format YYYY-MM")
        sys.exit(-1)

    try:
        year = int(year)
        month = int(month)
    except ValueError:
        print("Cannot parse created field.")
        sys.exit(-1)
        
    if year < 2019 or year > datetime.datetime.now().year:
        print("Invalid year.")
        sys.exit(-1)

    if month < 1 or month > 12:
        print("Invalid month.")
        sys.exit(-1)

    if manifest['gender'] not in GENDERS:
        print("Invalid gender. Must be one of: ", GENDERS)
        sys.exit(-1)
        
    if len(manifest['country']) != 2:
        print("Incorrect ID length")
        sys.exit(-1)

    if manifest['country'] not in COUNTRIES:
        print("Invalid country. Must be one of ", COUNTRIES)
        sys.exit(-1)

    try:
        age = int(manifest['age'])
    except ValueError:
        print("Cannot parse age.")
        sys.exit(-1)
        
    if age < 18 or age > 200:
        print("Invalid age. Must be 18-200")
        sys.exit(-1)

    if manifest['body_type'] not in BODY_TYPES:
        print("Invalid body type. Must be one of ", BODY_TYPES)
        sys.exit(-1)

    if manifest['mother'] not in ['true', 'false']:
        print("Invalid body type. Must be true or false.")
        sys.exit(-1)

    if len(manifest['ethnicity']) < MIN_ETHNICITY_LEN:
        print("ethnicify field too short. Must be at least %s characters. " % MIN_ETHNICITY_LEN)
        sys.exit(-1)

    if manifest['modification'] not in MODIFICATIONS:
        print("modification must be one of: ", MODIFICATIONS)
        sys.exit(-1)




@click.command()
@click.argument('hires', type=click.Path(exists=True))
@click.argument('surface', type=click.Path(exists=True))
@click.argument('manifest', type=click.Path(exists=True))
@click.argument('resolution')
@click.argument('dest', type=click.Path(exists=True))
def main(hires, surface, manifest, resolution, dest):

    try:
        with open(manifest, "rb") as m:
            manifest = json.loads(m.read())
    except IOError as err:
        print("Cannot read manifest file. IO error.", err)
        sys.exit(-1)

    validate_manifest(manifest)


if __name__ == "__main__":
    main();
