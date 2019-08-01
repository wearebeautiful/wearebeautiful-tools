import os
from flask import Flask, render_template, flash, url_for, current_app, redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import config
import json
from wearebeautiful.auth import init_auth
from wearebeautiful.redis import init_redis
from wearebeautiful.bundles import bundle_setup, load_bundle_data_into_redis


STATIC_PATH = "/static"
STATIC_FOLDER = "../static"
TEMPLATE_FOLDER = "../template"

auth = init_auth()

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)
app.secret_key = config.SECRET_KEY

Bootstrap(app)
app.redis = init_redis()

from wearebeautiful.views import bp as index_bp
from wearebeautiful.admin import bp as admin_bp
app.register_blueprint(index_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

bundle_setup(config.BUNDLE_DIR)
num = load_bundle_data_into_redis(app)
print("read %d bundles." % num)

@app.errorhandler(404)
def page_not_found(message):
    return render_template('errors/404.html', message=message), 404
