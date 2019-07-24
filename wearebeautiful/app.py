import os
from flask import Flask, render_template, flash, url_for, current_app, redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from random import uniform
import config
import json
from wearebeautiful.auth import init_auth


STATIC_PATH = "/static"
STATIC_FOLDER = "../static"
TEMPLATE_FOLDER = "../template"
BUNDLE_FOLDER = "../static/bundle"

auth = init_auth()

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)
app.secret_key = config.SECRET_KEY

Bootstrap(app)

from wearebeautiful.views import bp as index_bp
from wearebeautiful.admin import bp as admin_bp

app.register_blueprint(index_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')


bundles = []
try: 
    with open(os.path.join(BUNDLE_FOLDER, "bundles.json"), "r") as f:
        bundles = json.loads(f.read())
except IOError as err:
    print("ERROR: Cannot read bundles.json.", err)
except ValueError as err:
    print("ERROR: Cannot read bundles.json.", err)

app.bundles = {}
app.bundle_ids = []
for bundle in bundles:
    print("Add bundle ", bundle['id'])
    app.bundles[bundle['id']] = bundle
    app.bundle_ids.append(bundle['id'])

print("read %d bundles." % len(app.bundles))
