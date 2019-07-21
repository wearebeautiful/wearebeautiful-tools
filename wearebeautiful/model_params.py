#!/usr/bin/env python

import json
import click
import sys
import datetime
import os
import shutil
from zipfile import ZipFile
from tempfile import mkdtemp
from scale_mesh import scale_mesh

PRINT_FILE = "solid.obj"
SURFACE_FILE = "surface.obj"
SCREENSHOT_FILE = "screenshot.jpg"
MANIFEST_FILE = "manifest.json"

FORMAT_VERSION = 1 
REQUIRED_KEYS = [ "version", "id", "created", "gender", "country", "age", "body_type", 
                  "mother", "ethnicity", "released", "bodypart", "pose"]
OPTIONAL_KEYS = [ "pose_variant", "gender_comment", "comment", "other", "modification" ]
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
MIN_FREETEXT_FIELD = 5
MODIFICATIONS = ["none", "circumcised"," fgm", "labiaplasty", "masectomy", "female-to-male", "male-to-female", "breastfeeding", "pregnant", "episiotomy"]
MOTHER = ["no", "vaginal", "caesarean"]
BODYPART = [ "body", "bust", "breast", "nipple", "vulva", "buttocks", "penis" ]
POSE = ["normal", "aroused", "variant"]



def validate_date(date, partial=False):

    if partial:
        try:
            date_obj = datetime.datetime.strptime(date, '%Y-%m')
        except ValueError as err:
            print("Invalid date format. Must be YYYY-MM. (%s)" % err)
            return False

    else:
        try:
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError as err:
            print("Invalid date format. Must be YYYY-MM-DD. (%s)" % err)
            return False

    if date_obj.year < 2019 or date_obj.year > datetime.datetime.now().year:
        print("Invalid year.")
        return False

    return True


def validate_manifest(manifest):
    
    if manifest['version'] != FORMAT_VERSION:
        print("Incorrect format version. This script can only accept version %s" % FORMAT_VERSION)
        sys.exit(-1)

    if manifest.keys() in REQUIRED_KEYS:
        missing = list(set(REQUIRED_KEYS) - set(manifest.keys()))
        print("Some top level fields are missing. %s\n" % ",".join(missing))
        sys.exit(-1)

    if len(manifest['id']) != 6 or manifest['id'].isdigit():
        print("Incorrect ID length or non digits in ID.")
        sys.exit(-1)

    if not validate_date(manifest['created'], partial=True):
        print("Incorrect created date. Must be in YYYY-MM format and minimally specify year and month.")
        sys.exit(-1)

    if not validate_date(manifest['released']):
        print("Incorrect released date. Must be in YYYY-MM-DD format")
        sys.exit(-1)

    try:
        id = int(manifest['id'])
    except ValueError:
        print("Incorrect ID format. Must be a 4 digit number.")
        sys.exit(-1)


    if manifest['gender'] not in GENDERS:
        print("Invalid gender. Must be one of: ", GENDERS)
        sys.exit(-1)

    if manifest['bodypart'] not in BODYPART:
        print("Invalid bodypart. Must be one of: ", BODYPART)
        sys.exit(-1)

    if manifest['pose'] not in POSE:
        print("Invalid pose. Must be one of: ", POSE)
        sys.exit(-1)

    if manifest['pose'] == 'variant':
        if len(manifest['pose_variant']) < MIN_FREETEXT_FIELD:
            print("pose_variant field too short. Must be at least %d characters. " % MIN_FREETEXT_FIELD)
            sys.exit(-1)
        
    if manifest['pose'] != 'variant':
        if 'pose_variant' in manifest:
            print("pose_variant field must be blank when post not variant.")
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

    if manifest['mother'] not in MOTHER:
        print("Invalid value for the field mother. Must be one of ", MOTHER)
        sys.exit(-1)

    if len(manifest['ethnicity']) < MIN_FREETEXT_FIELD:
        print("ethnicity field too short. Must be at least %d characters. " % MIN_FREETEXT_FIELD)
        sys.exit(-1)

    if 'modification' in manifest:
        if type(manifest['modification']) != list:
            print("modification must be a list.")
            sys.exit(-1)

        if len(manifest['modification']) > 0 and manifest['modification'] not in MODIFICATIONS:
            print("modification must be one of: ", MODIFICATIONS)
            sys.exit(-1)

    return id



@click.command()
@click.argument('lresolution')
@click.argument('mresolution')
def main(lresolution, mresolution):

    manifest = os.path.join("/src", MANIFEST_FILE)
    surface = os.path.join("/src", SURFACE_FILE)
    solid = os.path.join("/src", PRINT_FILE)
    screenshot = os.path.join("/src", SCREENSHOT_FILE)

    try:
        with open(os.path.join("/src", manifest), "rb") as m:
            jmanifest = json.loads(m.read())
    except json.decoder.JSONDecodeError as err:
        print("Cannot parse manifest file. ", err)
        sys.exit(-1)
    except IOError as err:
        print("Cannot read manifest file. IO error.", err)
        sys.exit(-1)

    id = validate_manifest(jmanifest)

    tmp_dir = mkdtemp()
    low_res = os.path.join(tmp_dir, "surface-low.obj")
    medium_res = os.path.join(tmp_dir, "surface-medium.obj")

    if not os.path.exists(solid):
        solid = os.path.splitext(os.path.basename(solid))[0] + ".stl"
        solid = os.path.join("/src", solid)
        print("Could not find solid.obj, trying %s" % solid)
        if not os.path.exists(solid):
            print("Cannot find solid.obj or solid.stl");
            sys.exit(-1)

    if not os.path.exists(surface):
        surface = os.path.splitext(os.path.basename(surface))[0] + ".stl"
        surface = os.path.join("/src", surface)
        print("Could not find surface.obj, trying %s" % surface)
        if not os.path.exists(surface):
            print("Cannot find surface.obj or surface.stl");
            sys.exit(-1)

    try:
        scale_mesh(surface, low_res, float(lresolution))
        scale_mesh(surface, medium_res, float(mresolution))
    except IOError as err:
        print("Cannot down-scale mesh files. Error: ", err)
        sys.exit(-1)

    try:
        shutil.copy(solid, tmp_dir)
        shutil.copy(surface, tmp_dir)
        shutil.copy(screenshot, tmp_dir)
    except IOError as err:
        print("Cannot copy files. Error: ", err)
        sys.exit(-1)

    dest = os.path.join("/dest", "%04d-bundle.zip" % id)
    with ZipFile(dest, 'w') as zip:
        zip.write(manifest, arcname="manifest.json")
        zip.write(low_res, arcname="surface-low.obj")
        zip.write(medium_res, arcname="surface-medium.obj")
        zip.write(solid, arcname="solid.obj")
        zip.write(surface, arcname="surface-orig.obj")
        zip.write(screenshot, arcname="screenshot.jpg")

    shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    main();
