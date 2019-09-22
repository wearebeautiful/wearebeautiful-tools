#!/usr/bin/env python3

import os
import sys
import json
import zipfile
import datetime
import shutil
from wearebeautiful import model_params as param

MAX_SCREENSHOT_SIZE = 256000 # 256Kb is enough!

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


def bundle_code(id="", part="", pose="", arrangement="", excited="", manifest=None):

    if manifest:
        return "%s-%c%c%c%c" % (manifest['id'], 
                                param.BODY_PART[manifest['body_part']],
                                param.POSE[manifest['pose']],
                                param.ARRANGEMENT[manifest['arrangement']],
                                param.EXCITED[manifest['excited']])
    else:
        return "%0s-%c%c%c%c" % (id,  part, pose, arrangement, excited)


def parse_code(code):
    try:
        id, codes = code.split("-")
        if not id.isdigit() and len(id) == 6:
            raise ValueError

        if not len(codes) == 4:
            raise ValueError

        part, pose, arrangement, excited = list(codes)

    except ValueError:
        raise ValueError("Invalid model %s. Must be in format ######-CCCC." % code) 

    if part not in param.BODY_PART.values():
        raise ValueError("Invalid body part code '%c'" % part)

    if pose not in param.POSE.values():
        raise ValueError("Invalid pose code '%c'" % pose)

    if arrangement not in param.ARRANGEMENT.values():
        raise ValueError("Invalid arrangement code '%c'" % arrangement)

    if excited not in param.EXCITED.values():
        raise ValueError("Invalid excited code '%c'" % excited)

    return (id, part, pose, arrangement, excited)


def load_bundle_data_into_redis(app):
    ''' Read the bundles.json file and load into ram '''

    redis = app.redis
    bundles = []
    loaded_bundles = []
    try: 
        with open(os.path.join(bundle_dir, bundles_json_file), "r") as f:
            loaded_bundles = json.loads(f.read())
    except IOError as err:
        print("ERROR: Cannot read bundles.json.", err)
    except ValueError as err:
        print("ERROR: Cannot read bundles.json.", err)

    # Clean up old redis keys 
    for k in redis.scan_iter("m:*"):
        redis.delete(k)
    redis.delete("m:ids")
    redis.delete("b:index")

    # Now add new redis keys
    bundles = []
    ids = {}
    for bundle in loaded_bundles:
        code = bundle_code(manifest=bundle)
        redis.set("m:%s" % code, json.dumps(bundle))
        data = { 
            'id' : bundle['id'], 
            'body_part' : bundle['body_part'], 
            'body_type' : bundle['body_type'], 
            'gender' : bundle['gender'], 
            'age' : bundle['age'], 
            'country' : bundle['country'], 
            'pose' : bundle['pose'], 
            'arrangement' : bundle['arrangement'] ,
            'excited' : bundle['excited'],
            'code' : code
        }
        bundles.append(data)
        if not bundle['id'] in ids:
            ids[bundle['id']] = []
        ids[bundle['id']].append(data)

    redis.set("b:index", json.dumps(bundles))
    redis.set("m:ids", json.dumps(ids))

    return len(bundles)


def get_bundle_id_list(redis):
    """ Get the list of current ids """
    bundles = redis.get("b:index") or "[]"
    return json.loads(bundles)


def get_model_id_list(redis):
    """ Get the list of model ids """
    ids = redis.get("m:ids") or "{}"
    return json.loads(ids)


def get_bundle(redis, id, body_part, pose, arrangement, excited):
    """ Get the manifest of the given bundle """
    manifest = redis.get("m:%s" % bundle_code(id, body_part, pose, arrangement, excited))
    return json.loads(manifest)


def import_bundle(bundle_file):
    """ unzip and read bundle file """

    allowed_files = ['manifest.json', 'surface-low.stl', 'surface-medium.stl', 'solid.stl', 'surface-orig.stl', 'screenshot.jpg']
    try:
        zipf = zipfile.ZipFile(bundle_file)
    except zipfile.BadZipFile:
        return "Invalid zip file."

    files = zipf.namelist()
    for f in files:
        if not f in allowed_files:
            return "file %s is not part of a normal bundle. don't fuck it up, ok?" % f

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

    code = bundle_code(manifest=manifest)
    # The bundle looks ok, copy it into place
    dest_dir = os.path.join(bundle_dir, code)

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

    try:
        for member in allowed_files:
            print(os.path.join(dest_dir, member))
            zipf.extract(member, dest_dir)
    except IOError as err:
        print("IO error: ", err)
        return err

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

    for k in param.REQUIRED_KEYS:
        if k not in manifest.keys():
            return "required field %s is missing from manifest.json" % k

    for k in manifest.keys():
       if k not in param.REQUIRED_KEYS and k not in param.OPTIONAL_KEYS:
            return "top level field %s should not appear in manifest.json" % k

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

    if manifest['body_part'] not in param.BODY_PART:
        return "Invalid body_part. Must be one of: ", param.BODY_PART.keys()

    if manifest['pose'] not in param.POSE:
        return "Invalid pose. Must be one of: ", param.POSE.keys()

    if manifest['arrangement'] not in param.ARRANGEMENT:
        return "Invalid arrangement. Must be one of: ", param.ARRANGEMENT.keys()

    if manifest['excited'] not in param.EXCITED:
        return "Invalid excited. Must be one of: ", param.EXCITED.keys()

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
        if manifest['modification'] == "none":
            return "modification: 'none' is no longer supported. Please remove the modification line."

        if type(manifest['modification']) != list:
            return "modification must be a list."

        if len(manifest['modification']) > 0 and manifest['modification'] not in param.MODIFICATIONS:
            return "modification must be one of: ", param.MODIFICATIONS

    return ""
