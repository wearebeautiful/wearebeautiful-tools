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
