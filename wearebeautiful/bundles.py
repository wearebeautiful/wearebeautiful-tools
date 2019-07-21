#!/usr/bin/env python3

import os
import sys
import json
import zipfile


def read_bundle(bundles, bundle_file):
    try:
        with zipfile.ZipFile(bundle_file) as z:
            manifest_raw = z.read("manifest.json")
    except KeyError:
        print("Cannot read manifest from %s." % bundle_file)
        return

    manifest = json.loads(manifest_raw) 
    bundles.append(manifest)


def parse_bundles(bundle_dir):
    bundles = []

    for f in os.listdir(bundle_dir):
        if f.endswith(".zip"):
            read_bundle(bundles, os.path.join(bundle_dir, f))

    return bundles


def create_bundle_index(bundle_dir, bundle_file):
    bundles = parse_bundles(bundle_dir)
    with open(bundle_file, "w") as out:
        out.write(json.dumps(bundles))


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
    
    if manifest['version'] != param.FORMAT_VERSION:
        print("Incorrect format version. This script can only accept version %s" % param.FORMAT_VERSION)
        sys.exit(-1)

    if manifest.keys() in param.REQUIRED_KEYS:
        missing = list(set(param.REQUIRED_KEYS) - set(manifest.keys()))
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


    if manifest['gender'] not in param.GENDERS:
        print("Invalid gender. Must be one of: ", param.GENDERS)
        sys.exit(-1)

    if manifest['bodypart'] not in param.BODYPART:
        print("Invalid bodypart. Must be one of: ", param.BODYPART)
        sys.exit(-1)

    if manifest['pose'] not in param.POSE:
        print("Invalid pose. Must be one of: ", param.POSE)
        sys.exit(-1)

    if manifest['pose'] == 'variant':
        if len(manifest['pose_variant']) < param.MIN_FREETEXT_FIELD_LEN:
            print("pose_variant field too short. Must be at least %d characters. " % param.MIN_FREETEXT_FIELD_LEN)
            sys.exit(-1)
        
    if manifest['pose'] != 'variant':
        if 'pose_variant' in manifest:
            print("pose_variant field must be blank when post not variant.")
            sys.exit(-1)
        
    if len(manifest['country']) != 2:
        print("Incorrect ID length")
        sys.exit(-1)

    if manifest['country'] not in param.COUNTRIES:
        print("Invalid country. Must be one of ", param.COUNTRIES)
        sys.exit(-1)

    try:
        age = int(manifest['age'])
    except ValueError:
        print("Cannot parse age.")
        sys.exit(-1)
        
    if age < 18 or age > 200:
        print("Invalid age. Must be 18-200")
        sys.exit(-1)

    if manifest['body_type'] not in param.BODY_TYPES:
        print("Invalid body type. Must be one of ", param.BODY_TYPES)
        sys.exit(-1)

    if manifest['mother'] not in param.MOTHER:
        print("Invalid value for the field mother. Must be one of ", param.MOTHER)
        sys.exit(-1)

    if len(manifest['ethnicity']) < param.MIN_FREETEXT_FIELD_LEN:
        print("ethnicity field too short. Must be at least %d characters. " % param.MIN_FREETEXT_FIELD_LEN)
        sys.exit(-1)

    if 'modification' in manifest:
        if type(manifest['modification']) != list:
            print("modification must be a list.")
            sys.exit(-1)

        if len(manifest['modification']) > 0 and manifest['modification'] not in param.MODIFICATIONS:
            print("modification must be one of: ", param.MODIFICATIONS)
            sys.exit(-1)

    return id

