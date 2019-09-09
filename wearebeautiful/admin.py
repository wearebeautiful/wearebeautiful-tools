import os
import zipfile
import shutil
from random import uniform
from flask import render_template, current_app, redirect, Blueprint, request, Response
from werkzeug.exceptions import BadRequest, InternalServerError
import tempfile
import config
import json
from io import StringIO
import subprocess
from wearebeautiful.auth import _auth as auth
from wearebeautiful.bundles import create_bundle_index, load_bundle_data_into_redis, import_bundle, \
                            get_model_id_list
from wearebeautiful.model_params import LOW_RES_SEGMENT_LEN, MEDIUM_RES_SEGMENT_LEN

NEW_BUNDLE_DIR = "static/new_bundles"

bp = Blueprint('admin', __name__)

@bp.route('/')
@auth.login_required
def admin():
    return render_template("admin/index.html")


@bp.route('/new')
@auth.login_required
def admin_new():
    models = get_model_id_list(current_app.redis)
    while True:
        new_id = int(uniform(100000, 999999))
        if new_id not in models:
            return render_template("admin/new.html", new_id = new_id)


@bp.route('/upload', methods=['GET'])
@auth.login_required
def admin_upload_get():

    files = os.listdir(NEW_BUNDLE_DIR)
    links = []
    for f in files:
        links.append(("/static/new_bundles/" + f, f))

    return render_template("admin/upload.html", links=links)


@bp.route('/upload', methods=['POST'])
@auth.login_required
def admin_upload_post():
    if 'file' not in request.files:
        raise BadRequest(response=Response(response="Request is missing file part.", status=400))

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
        raise InternalServerError(response=Response(response="Cannot save bundle to disk: %s" % str(err), status=400))

    err = import_bundle(filename.name)
    if err:
        raise BadRequest(response=Response(response=err, status=400))
        
    try:
        filename.close()
    except Exception:
        pass

    create_bundle_index()
    load_bundle_data_into_redis(current_app)

    return ""

@bp.route('/upload-raw', methods=['POST'])
@auth.login_required
def admin_upload_raw__post():

    if not current_app.debug:
        raise BadRequest(response=Response(response="Cannot make bundles on production server.", status=400))

    if 'file' not in request.files:
        raise BadRequest(response=Response(response="Request is missing file part.", status=400))

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
        raise InternalServerError(response=Response(response="Cannot save bundle to disk: %s" % str(err), status=500))


    required_files = ['manifest.json', 'solid.stl', 'surface.stl', 'screenshot.jpg']
    try:
        zipf = zipfile.ZipFile(filename)
    except zipfile.BadZipFile:
        return "Invalid zip file."

    files = zipf.namelist()
    for f in required_files:
        if f not in files:
            raise InternalServerError(response=Response(response="missing file %s in input zip file." % f, status=500))


    tmp_dir = os.path.join(NEW_BUNDLE_DIR, "tmp")
    try:
        os.makedirs(tmp_dir)
    except FileExistsError:
        pass
    except IOError:
        raise InternalServerError(response=Response(response="Cannot create new bundle dir", status=500))


    try:
        for member in required_files:
            zipf.extract(member, tmp_dir)
    except IOError as err:
        raise InternalServerError(response=Response(response=err, status=500))

    cp = subprocess.run(["bin/make_bundle.sh", "%f" % LOW_RES_SEGMENT_LEN, "%f" % MEDIUM_RES_SEGMENT_LEN, tmp_dir, 
        "static/new_bundles"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode == 137:
        raise BadRequest(response=Response(response=str("OOM: out of memory."), status=500))
    if cp.returncode != 0:
        raise BadRequest(response=Response(response=str(cp.stdout), status=400))

    print(cp.stdout)

    try:
        shutil.rmtree(tmp_dir)
    except IOError as err:
        raise InternalServerError(response=Response(response="Failed to erase tmp files", status=500))

    try:
        filename.close()
    except Exception:
        pass

    return Response(str(cp.stdout.decode("utf-8")), 200)
