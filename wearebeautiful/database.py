import os
import json
import shutil

from peewee import SqliteDatabase
from wearebeautiful.db_model import DBModel, db, create_from_manifest
from wearebeautiful.manifest import validate_manifest
import config

DB_FILE = "wab-models.db"
MIN_SURFACE_MED_SIZE = 8 * 1024 * 1024
MAX_SURFACE_MED_SIZE = 12 * 1024 * 1024
MIN_SURFACE_LOW_SIZE = 1.5 * 1024 * 1024
MAX_SURFACE_LOW_SIZE = 5 * 1024 * 1024

def add_models(dir):
    for item in os.listdir(dir):
        if item.endswith(".json"): 
            with(open(os.path.join(dir, item), "rb")) as m:
                try:
                    manifest = json.loads(str(m.read().decode('utf-8')))
                except json.decoder.JSONDecodeError as err:
                    print("  skipping %s: %s" % (item, str(err)))
                    continue
                except IOError as err:
                    print("  skipping %s: %s" % (item, str(err)))
                    continue

            err = validate_manifest(manifest)
            if err:
                print("  manifest not valid, skipping: %s" % err)
                continue

            model = create_from_manifest(manifest)
            print("  add %s-%s-%d " % (model.model_id, model.code, model.version), end = '')
            model.save()

            surface_med = os.path.join(config.MODEL_DIR, model.model_id, model.code, "%s-%s-%d-surface-med.stl" % (model.model_id, model.code, model.version))
            surface_med_size = os.path.getsize(surface_med)
            if surface_med_size > MAX_SURFACE_MED_SIZE:
                med_size_warn = '+'
            elif surface_med_size < MIN_SURFACE_MED_SIZE:
                med_size_warn = '-'
            else:
                med_size_warn = ' '

            surface_low = os.path.join(config.MODEL_DIR, model.model_id, model.code, "%s-%s-%d-surface-low.stl" % (model.model_id, model.code, model.version))
            surface_low_size = os.path.getsize(surface_low)
            if surface_low_size > MAX_SURFACE_LOW_SIZE:
                low_size_warn = '+'
            elif surface_low_size < MIN_SURFACE_LOW_SIZE:
                low_size_warn = '-'
            else:
                low_size_warn = ' '

            print(" med: %5.2f MB %s " % (surface_med_size / 1024.0 / 1024.0, med_size_warn), end = '')
            print(" low: %5.2f MB %s " % (surface_low_size / 1024.0 / 1024.0, low_size_warn), end = '')

            screenshot = os.path.join(config.MODEL_GIT_DIR, model.model_id, model.code, "%s-%s-%d-screenshot.jpg" % (model.model_id, model.code, model.version))
            if not os.path.exists(screenshot):
                print(" (warning: %s is missing)" % screenshot)
            else:
                print()






def add_human_model(dir):
    for item in os.listdir(dir):
        dir_name = os.path.join(dir, item)
        if len(item) == 4 and not item.isdigit():
            add_models(dir_name)


def create_database():

    db_file = os.path.join(config.MODEL_GIT_DIR, DB_FILE)
    print("creating db file '%s'" % db_file)
    try:
        os.unlink(db_file)
    except OSError:
        pass

    db.init(db_file)
    db.create_tables([DBModel])
    for item in os.listdir(config.MODEL_DIR):
        dir_name = os.path.join(config.MODEL_DIR, item)
        if len(item) == 6 and item.isdigit() and os.path.isdir(dir_name):
            add_human_model(dir_name)

    db_file_non_git = os.path.join(config.MODEL_DIR, DB_FILE)
    shutil.copyfile(db_file, db_file_non_git)
