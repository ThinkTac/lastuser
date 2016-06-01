# -*- coding: utf-8 -*-

import unittest
from lastuserapp import app, db, init_for
from .fixtures import make_fixtures


class TestDatabaseFixture(unittest.TestCase):
    def setUp(self):
        init_for('testing')
        app.config['TESTING'] = True
        db.app = app
        db.create_all()
        self.db = db

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        db.session.remove()
