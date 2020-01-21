#!/usr/bin/env python3

import os
import sys
import json
import zipfile
import datetime
import shutil
from wearebeautiful import model_params as param

MAX_SCREENSHOT_SIZE = 256000 # 256Kb is enough!


def make_code(id="", part="", pose="", arrangement="", excited="", manifest=None):

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

    if manifest['body_type'] not in param.BODY_TYPES:
        return "Invalid body type. Must be one of ", param.BODY_TYPES

    if manifest['mother'] not in param.MOTHER:
        return "Invalid value for the field mother. Must be one of ", param.MOTHER

    if 'modification' in manifest:
        if manifest['modification'] == "none":
            return "modification: 'none' is no longer supported. Please remove the modification line."

        if type(manifest['modification']) != list:
            return "modification must be a list."

        for mod in manifest['modification']:
            if mod not in param.MODIFICATIONS:
                return "modification must be one of: ", param.MODIFICATIONS

    return ""