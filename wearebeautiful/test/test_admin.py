import os
import flask_testing
from flask import url_for
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

from wearebeautiful.app import app
from utils import ServerTestCase

class IndexViewsTestCase(ServerTestCase):

    def setUp(self):
        ServerTestCase.setUp(self)

    def test_admin(self):
        resp = self.client.get(url_for('admin.admin_new'))
        self.assert200(resp)

    def test_admin_upload(self):
        resp = self.client.get(url_for('admin.admin_upload_get'))
        self.assert200(resp)

    def test_admin_new(self):
        resp = self.client.get(url_for('admin.admin_new'))
        self.assert200(resp)

    # TODO ADD upload_post test
