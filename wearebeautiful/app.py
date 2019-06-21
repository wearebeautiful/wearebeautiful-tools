import os
from flask import Flask, render_template, flash, url_for
from flask_bootstrap import Bootstrap
import config
import json

STATIC_PATH = "/static"
STATIC_FOLDER = "../static"
TEMPLATE_FOLDER = "../template"
BUNDLE_FOLDER = "bundle"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)
app.secret_key = config.SECRET_KEY
Bootstrap(app)

try: 
    with open(os.path.join(BUNDLE_FOLDER, "bundles.json"), "r") as f:
        bundles = json.loads(f.read())
except IOError as err:
    print("ERROR: Cannot read bundles.json.", err)
except ValueError as err:
    print("ERROR: Cannot read bundles.json.", err)

app.bundles = {}
for bundle in bundles:
    app.bundles[bundle['id']] = bundle

print("read %d bundles." % len(app.bundles))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/browse')
def browse():
    return render_template("browse.html", bundles = app.bundles)

@app.route('/team')
def team():
    return render_template("team.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/view/')
def view_root():
    flash('You need to provide a model id to view.')
    return render_template("error.html")

@app.route('/view/<model>')
def view(model):
    if model == '-':
        return render_template("view.html", manifest = {'id':''})

    return render_template("view.html", manifest = app.bundles[model])


@app.route('/company')
def company():
    return render_template("company.html")

@app.route('/donate')
def donate():
    return render_template("donate.html")
