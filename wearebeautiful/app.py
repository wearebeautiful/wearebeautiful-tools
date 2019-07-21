import os
from flask import Flask, render_template, flash, url_for, current_app
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from random import uniform
import config
import json

STATIC_PATH = "/static"
STATIC_FOLDER = "../static"
TEMPLATE_FOLDER = "../template"
BUNDLE_FOLDER = "../static/bundle"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)
app.secret_key = config.SECRET_KEY
Bootstrap(app)

auth = HTTPBasicAuth()
users = {
    config.SITE_USERNAME :  generate_password_hash(config.SITE_PASSWORD),
}


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

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@app.route('/')
@auth.login_required
def index():
    return render_template("index.html")

@app.route('/browse')
@auth.login_required
def browse():
    return render_template("browse.html", bundles = app.bundles)

@app.route('/team')
@auth.login_required
def team():
    return render_template("team.html")

@app.route('/about')
@auth.login_required
def about():
    return render_template("about.html")

@app.route('/view/')
@auth.login_required
def view_root():
    flash('You need to provide a model id to view.')
    return render_template("error.html")

@app.route('/view/<model>')
@auth.login_required
def view(model):
    if model == '-':
        return render_template("view.html", manifest = {'id':''})

    return render_template("view.html", manifest = app.bundles[model])

@app.route('/company')
@auth.login_required
def company():
    return render_template("company.html")


@app.route('/donate')
@auth.login_required
def donate():
    return render_template("donate.html")


@app.route('/admin')
@auth.login_required
def admin():
    return render_template("admin/index.html")


@app.route('/admin/new')
@auth.login_required
def admin_new():
    while True:
        new_id = int(uniform(100000, 999999))
        if new_id not in current_app.bundle_ids:
            return render_template("admin/new.html", new_id = new_id)


@app.route('/admin/upload')
@auth.login_required
def admin_upload():
    return render_template("admin/upload.html")
