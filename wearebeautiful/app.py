from flask import Flask, render_template
from flask_bootstrap import Bootstrap

STATIC_PATH = "/static"
STATIC_FOLDER = "../static"
TEMPLATE_FOLDER = "../template"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)
Bootstrap(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/team')
def team():
    return render_template("team.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/view')
def browse():
    return render_template("view.html")

@app.route('/company')
def company():
    return render_template("company.html")
