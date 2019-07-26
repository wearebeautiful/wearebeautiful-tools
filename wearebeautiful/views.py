from werkzeug.exceptions import NotFound
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint
from wearebeautiful.auth import _auth as auth
from wearebeautiful.bundles import get_bundle_id_list, get_bundle
import config

bp = Blueprint('index', __name__)

@bp.route('/')
@auth.login_required
def index():
    return render_template("index.html")


@bp.route('/browse')
@auth.login_required
def browse():
    return render_template("browse.html", bundles = get_bundle_id_list(current_app.redis))


@bp.route('/team')
@auth.login_required
def team():
    return render_template("team.html")


@bp.route('/about')
@auth.login_required
def about():
    return render_template("about.html")


@bp.route('/view/')
@auth.login_required
def view_root():
    flash('You need to provide a model id to view.')
    return render_template("error.html")


@bp.route('/view/<model>')
@auth.login_required
def view(model):
    if model == '-':
        return render_template("view.html", manifest = {'id':''})

    bundle = get_bundle(current_app.redis, model)
    if not bundle:
        raise NotFound("Model %s not found." % model)

    return render_template("view.html", manifest = bundle)

    
@bp.route('/company')
@auth.login_required
def company():
    return render_template("company.html")


@bp.route('/donate')
@auth.login_required
def donate():
    return render_template("donate.html")
