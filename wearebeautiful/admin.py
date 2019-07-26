import os
import zipfile
from flask import render_template, current_app, redirect, Blueprint, request
from werkzeug.exceptions import BadRequest
import tempfile
import config
import json
from io import StringIO
from wearebeautiful.auth import _auth as auth
from wearebeautiful.bundles import create_bundle_index, load_bundle_data_into_redis, import_bundle

bp = Blueprint('admin', __name__)

@bp.route('/')
@auth.login_required
def admin():
    return render_template("admin/index.html")


@bp.route('/new')
@auth.login_required
def admin_new():
    while True:
        new_id = int(uniform(100000, 999999))
        if new_id not in current_app.bundle_ids:
            return render_template("admin/new.html", new_id = new_id)


@bp.route('/upload', methods=['GET'])
@auth.login_required
def admin_upload_get():
    return render_template("admin/upload.html")


@bp.route('/upload', methods=['POST'])
@auth.login_required
def admin_upload_post():
    if 'file' not in request.files:
        raise BadRequest("Request is missing file part.")

    try: 
        f = request.files['file']
        filename = tempfile.NamedTemporaryFile()
        f.save(filename.name)
    except IOError as err:
        if filename.name:
            try:
                os.unlink(filename.name)
            except Exception:
                pass
        raise InternalServerError("Cannot save bundle to disk: ", err)

    err = import_bundle(filename.name)
    if err:
        print(err)
        raise BadRequest(err)
        
    try:
        filename.close()
    except Exception:
        pass

    create_bundle_index()
    load_bundle_data_into_redis(current_app)

    return ""
