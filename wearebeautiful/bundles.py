#!/usr/bin/env python3

import os
import sys
import json
import zipfile
import datetime
import shutil
import config
from wearebeautiful import model_params as param

bundle_dir = config.BUNDLE_DIR

def bundle_setup():
    ''' Make the bundle dir, in case it doesn't exist '''
    try:
        os.makedirs(bundle_dir)
    except FileExistsError:
        pass


def read_bundle_index():
    ''' Read the bundles '''
    bundles = []
    bundle_ids = []
    try: 
        with open(os.path.join(bundle_dir, "bundles.json"), "r") as f:
            bundles = json.loads(f.read())
    except IOError as err:
        print("ERROR: Cannot read bundles.json.", err)
    except ValueError as err:
        print("ERROR: Cannot read bundles.json.", err)

    return bundles
    return bundles, bundle_ids


def read_bundle(bundles, bundle_file):
    try:
        with zipfile.ZipFile(bundle_file) as z:
            manifest_raw = z.read("manifest.json")
    except KeyError:
        print("Cannot read manifest from %s." % bundle_file)
        return

    manifest = json.loads(manifest_raw) 
    bundles.append(manifest)


def parse_bundles():
    bundles = []

    for f in os.listdir(bundle_dir):
        if f.endswith(".zip"):
            read_bundle(bundles, os.path.join(bundle_dir, f))

    return bundles


def create_bundle_index(bundle_file):
    bundles = parse_bundles(bundle_dir)
    with open(bundle_file, "w") as out:
        out.write(json.dumps(bundles))


def read_bundle_index():
    bundles = {}
    bundle_ids = []
    for bundle in read_bundles():
        print("Add bundle ", bundle['id'])
        bundles[bundle['id']] = bundle
        bundle_ids.append(bundle['id'])



def import_bundle(bundle_file):
    """ unzip and read bundle file """

    print("Check files")
    allowed_files = ['manifest.json', 'surface-low.obj', 'surface-medium.obj', 'solid.obj', 'surface-orig.obj', 'screenshot.jpg']
    try:
        zipf = zipfile.ZipFile(bundle_file)
    except zipfile.BadZipFile:
        return "Invalid zip file."

    files = zipf.namelist()
    if allowed_files != files:
        return "Incorrect files in the bundle."

    print("read and verify manifest")
    try:
        rmanifest = zipf.read("manifest.json")
    except IOError:
        return "Cannot read manifest.json"

    try:
        manifest = json.loads(rmanifest)
    except json.decoder.JSONDecodeError as err:
        return err

    err = validate_manifest(manifest)
    if err:
        return err

    # The bundle looks ok, copy it into place
    dest_dir = os.path.join(bundle_dir, manifest['id'])

    print("create bundle dir", dest_dir)
    while True:
        try:
            os.mkdir(dest_dir)
            break
        except FileExistsError:
            try:
                shutil.rmtree(dest_dir)
            except IOError as err:
                print("Failed to erase old bundle.", err)
                return err

    print("copy files")
    try:
        for member in allowed_files:
            print(os.path.join(dest_dir, member))
            zipf.extract(member, os.path.join(dest_dir, member))
    except IOError as err:
        print("IO error: ", err)
        return err

    print("done import bundle")

    return ""


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
        return "Incorrect format version. This script can only accept version %s" % param.FORMAT_VERSION

    if manifest.keys() in param.REQUIRED_KEYS:
        missing = list(set(param.REQUIRED_KEYS) - set(manifest.keys()))
        return "Some top level fields are missing. %s\n" % ",".join(missing)

    if len(manifest['id']) != 6 or not manifest['id'].isdigit():
        return "Incorrect ID length or non digits in ID."

    if not validate_date(manifest['created'], partial=True):
        return "Incorrect created date. Must be in YYYY-MM format and minimally specify year and month."

    if not validate_date(manifest['released']):
        return "Incorrect released date. Must be in YYYY-MM-DD format"

    try:
        id = int(manifest['id'])
    except ValueError:
        return "Incorrect ID format. Must be a 4 digit number."


    if manifest['gender'] not in param.GENDERS:
        return "Invalid gender. Must be one of: ", param.GENDERS

    if manifest['bodypart'] not in param.BODYPART:
        return "Invalid bodypart. Must be one of: ", param.BODYPART

    if manifest['pose'] not in param.POSE:
        return "Invalid pose. Must be one of: ", param.POSE

    if manifest['pose'] == 'variant':
        if len(manifest['pose_variant']) < param.MIN_FREETEXT_FIELD_LEN:
            return "pose_variant field too short. Must be at least %d characters. " % param.MIN_FREETEXT_FIELD_LEN
        
    if manifest['pose'] != 'variant':
        if 'pose_variant' in manifest:
            return "pose_variant field must be blank when post not variant."
        
    if len(manifest['country']) != 2:
        return "Incorrect ID length"

    if manifest['country'] not in param.COUNTRIES:
        return "Invalid country. Must be one of ", param.COUNTRIES

    try:
        age = int(manifest['age'])
    except ValueError:
        return "Cannot parse age."
        
    if age < 18 or age > 200:
        return "Invalid age. Must be 18-200"

    if manifest['body_type'] not in param.BODY_TYPES:
        return "Invalid body type. Must be one of ", param.BODY_TYPES

    if manifest['mother'] not in param.MOTHER:
        return "Invalid value for the field mother. Must be one of ", param.MOTHER

    if len(manifest['ethnicity']) < param.MIN_FREETEXT_FIELD_LEN:
        return "ethnicity field too short. Must be at least %d characters. " % param.MIN_FREETEXT_FIELD_LEN

    if 'modification' in manifest:
        if type(manifest['modification']) != list:
            return "modification must be a list."

        if len(manifest['modification']) > 0 and manifest['modification'] not in param.MODIFICATIONS:
            return "modification must be one of: ", param.MODIFICATIONS

    return ""
