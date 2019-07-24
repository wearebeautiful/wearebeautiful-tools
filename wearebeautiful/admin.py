import os
from flask import render_template, current_app, redirect, Blueprint
import config
import json
from wearebeautiful.auth import _auth as auth

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
    return ""
