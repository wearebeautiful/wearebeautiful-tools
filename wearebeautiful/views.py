from werkzeug.exceptions import NotFound
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint
from wearebeautiful.auth import _auth as auth
from wearebeautiful.bundles import get_bundle_id_list, get_bundle, get_model_id_list
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


@bp.route('/view')
@auth.login_required
def view_simple():
    return redirect(url_for("index.browse"))

@bp.route('/view/<model>')
@auth.login_required
def view(model):
    if model == '-':
        return render_template("view.html", manifest = {'id':''})

    if model.isdigit() and len(model) == 6:
        model_list = get_model_id_list(current_app.redis)
        for key in model_list.keys():
            bundles = model_list[key]
            for bundle in bundles:
                bundle['model-str'] = "%s-%s-%s" % (bundle['id'], bundle['bodypart'], bundle['pose'])
        if model not in model_list:
            raise NotFound("Model %s does not exist." % model)
        else:
            if len(model_list[model]) == 1:
                return redirect(url_for("index.view", model=model_list[model][0]['model-str']))
            else:
                return render_template("bundle-disambig.html", model=model, model_list=model_list[model])

    try:
        id, bodypart, pose = model.split("-")
    except ValueError:
        raise NotFound("Model %s does not exist." % model)
        
    bundle = get_bundle(current_app.redis, id, bodypart, pose)
    if not bundle:
        raise NotFound("Model %s not found, when it should've been found. Oops, this is bad. " % model)

    return render_template("view.html", manifest = bundle)

    
@bp.route('/company')
@auth.login_required
def company():
    return render_template("company.html")


@bp.route('/donate')
@auth.login_required
def donate():
    return render_template("donate.html")
