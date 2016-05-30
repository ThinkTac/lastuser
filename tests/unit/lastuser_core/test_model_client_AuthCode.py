from lastuserapp import db
import lastuser_core.models as models
from .test_db import TestDatabaseFixture
from datetime import datetime, timedelta

class TestAuthCode(TestDatabaseFixture):

    def test_authcode(self):
        """Test to verify creation of AuthCode instance"""
        crusoe = self.fixtures.crusoe
        client = self.fixtures.client
        redirect_uri=u'http://batdogadventures.com/fun'
        scope=u'id'
        auth_code = models.AuthCode(user=crusoe, client=client, redirect_uri=redirect_uri, scope=scope)
        db.session.add(auth_code)
        db.session.commit()
        result = models.AuthCode.query.filter_by(user=crusoe).one_or_none()
        self.assertIsInstance(result, models.AuthCode)
        self.assertEqual(result.client, client)
        self.assertEqual(result.user, crusoe)
        self.assertEqual(result.redirect_uri, redirect_uri)
        self.assertTrue(hasattr(result, 'code'))

    def test_authcode_is_valid(self):
        """Test to verify if a AuthCode instance is valid"""
        oakley = self.fixtures.oakley
        client = self.fixtures.client
        auth_code = models.AuthCode(user=oakley, client=client, used=True, redirect_uri=u'http://batdogadventures.com/fun', scope=u'email')
        db.session.add(auth_code)
        db.session.commit()

        # Scenario 1: When code has not been used
        unused_code_status = models.AuthCode.query.filter_by(user=oakley).one_or_none().is_valid()
        self.assertFalse(unused_code_status)

        # Scenario 2: When code has been used
        auth_code.created_at = datetime.utcnow()
        auth_code.used = False
        db.session.commit()
        used_code_status = models.AuthCode.query.filter_by(user=oakley).one_or_none().is_valid()
        self.assertTrue(used_code_status)
