import os
import flask_testing
from flask import url_for
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

from wearebeautiful.app import app
from utils import ServerTestCase

class IndexViewsTestCase(ServerTestCase):

    def setUp(self):
        ServerTestCase.setUp(self)

    def test_index(self):
        resp = self.client.get(url_for('index.index'))
        self.assert200(resp)

    def test_team(self):
        resp = self.client.get(url_for('index.team'))
        self.assert200(resp)

    def test_about(self):
        resp = self.client.get(url_for('index.about'))
        self.assert200(resp)

    def test_company(self):
        resp = self.client.get(url_for('index.company'))
        self.assert200(resp)

    def test_donate(self):
        resp = self.client.get(url_for('index.donate'))
        self.assert200(resp)

    def test_browse(self):
        resp = self.client.get(url_for('index.browse'))
        self.assert200(resp)

    def test_view_no_model(self):
        resp = self.client.get(url_for('index.view_simple'))
        self.assert_status(resp, 308)

    def test_view_empty(self):
        resp = self.client.get(url_for('index.view', model="-"))
        self.assert200(resp)

    def test_view(self):
        resp = self.client.get(url_for('index.view', model="-"))
        self.assert200(resp)

    # TODO Add more browse and view testing
