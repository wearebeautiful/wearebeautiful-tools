from werkzeug.exceptions import NotFound
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint
from wearebeautiful.auth import _auth as auth
from wearebeautiful.bundles import get_bundle_id_list, get_bundle, get_model_id_list, parse_code
import config

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    if auth.username():
        return render_template("index.html")
    else:
        return redirect(url_for("index.soon"))


@bp.route('/soon')
def soon():
    return render_template("coming-soon.html", bare=True)


@bp.route('/browse')
@auth.login_required
def browse():
    bundles = get_bundle_id_list(current_app.redis)

    sections = { }
    order = sorted(list(set([ x['body_part'] for x in bundles])))
    for section in order:
        sections[section] = { 
            'name' : section[0].upper() + section[1:],
            'bundles' : []
        }                  
    sections['other'] =  { 'name' : "Other", 'bundles' : [] }
    order.append('other')

    for bundle in bundles:
        if bundle['id'] == '000000':
            sections['other']['bundles'].append(bundle)
        else:
            sections[bundle['body_part']]['bundles'].append(bundle)

    return render_template("browse.html", order = order, sections = sections)


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

@bp.route('/statistics')
@auth.login_required
def statistics():
    return render_template("statistics.html")

@bp.route('/view/<model>')
@auth.login_required
def view(model):
    if model == '-':
        return render_template("view.html", manifest = {'id':''})

    if model.isdigit() and len(model) == 6:
        model_list = get_model_id_list(current_app.redis)
        if model not in model_list:
            raise NotFound("Model %s does not exist." % model)
        else:
            if len(model_list[model]) == 1:
                return redirect(url_for("index.view", model=model_list[model][0]['code']))
            else:
                return render_template("bundle-disambig.html", model=model, model_list=model_list[model])

    try:
        (id, part, pose, arrangement, excited) = parse_code(model)
        
    except ValueError as err:
        raise NotFound(err)
        
    bundle = get_bundle(current_app.redis, id, part, pose, arrangement, excited)
    if not bundle:
        raise NotFound("Model %s not found, when it should've been found. Oops, this is bad. " % model)

    return render_template("view.html", manifest = bundle, code=model)

    
@bp.route('/company')
@auth.login_required
def company():
    return render_template("company.html")


@bp.route('/donate')
@auth.login_required
def donate():
    return render_template("donate.html")
