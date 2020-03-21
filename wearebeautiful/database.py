import os
import json
import shutil

from peewee import SqliteDatabase
from wearebeautiful.db_model import DBModel, db, create_from_manifest
from wearebeautiful.manifest import validate_manifest
import config

DB_FILE = "wab-models.db"

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

            print("  add ",dir)
            model = create_from_manifest(manifest)
            model.save()


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
