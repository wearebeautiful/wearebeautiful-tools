#!/usr/bin/env python3

import os
import sys
import json
import zipfile
import datetime
import shutil
from wearebeautiful import model_params as param

bundles_json_file = "bundles.json"

def bundle_setup(bundle_dir_arg):
    ''' Make the bundle dir, in case it doesn't exist '''

    global bundle_dir
    bundle_dir = bundle_dir_arg
    try:
        os.makedirs(bundle_dir)
    except FileExistsError:
        pass


def create_bundle_index():
    ''' Iterate the bundles directory and read the manifest files '''

    bundles = []
    for path in os.listdir(bundle_dir):
        if path[0:6].isdigit() and path[6] == '-':
            with open(os.path.join(bundle_dir, path, "manifest.json"), "r") as f:
                manifest = json.loads(f.read())
                bundles.append(manifest)

    with open(os.path.join(bundle_dir, bundles_json_file), "w") as out:
        out.write(json.dumps(bundles))

    return bundles


def load_bundle_data_into_redis(app):
    ''' Read the bundles.json file and load into ram '''

    redis = app.redis
    bundles = []
    try: 
        with open(os.path.join(bundle_dir, bundles_json_file), "r") as f:
            bundles = json.loads(f.read())
    except IOError as err:
        print("ERROR: Cannot read bundles.json.", err)
    except ValueError as err:
        print("ERROR: Cannot read bundles.json.", err)

    # Clean up old redis keys 
    for k in redis.scan_iter("m:*"):
        redis.delete(k)
    redis.delete("b:ids")

    # Now add new redis keys
    ids = []
    for bundle in bundles:
        redis.set("m:%s:%s:%s" % (bundle['id'], bundle['bodypart'], bundle['pose']), json.dumps(bundle))
        ids.append({ 'id' : bundle['id'], 'bodypart' : bundle['bodypart'], 'pose' : bundle['pose'] })

    redis.set("b:ids", json.dumps(ids))
    print(json.dumps(ids))

    return len(ids)


def get_bundle_id_list(redis):
    """ Get the list of current ids """
    bundles = redis.get("b:ids") or ""
    return json.loads(bundles)


def get_bundle(redis, id, bodypart, pose):
    """ Get the manifest of the given bundle """
    manifest = redis.get("m:%s:%s:%s" % (id, bodypart, pose))
    return json.loads(manifest)


def import_bundle(bundle_file):
    """ unzip and read bundle file """

    allowed_files = ['manifest.json', 'surface-low.obj', 'surface-medium.obj', 'solid.obj', 'surface-orig.obj', 'screenshot.jpg']
    try:
        zipf = zipfile.ZipFile(bundle_file)
    except zipfile.BadZipFile:
        return "Invalid zip file."

    files = zipf.namelist()
    if allowed_files != files:
        return "Incorrect files in the bundle."

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
    dest_dir = os.path.join(bundle_dir, "%s-%s-%s" % (manifest['id'], manifest['bodypart'], manifest['pose']))

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
            zipf.extract(member, dest_dir)
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
