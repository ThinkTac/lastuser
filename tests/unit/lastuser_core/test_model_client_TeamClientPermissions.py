from lastuserapp import db
import lastuser_core.models as models
from .test_db import TestDatabaseFixture
import fixtures


class TestTeamClientPermissions(TestDatabaseFixture):

    def test_TeamClientPermissions(self):
        """Test for verifying creation of TeamClientPermissions' instance"""
        result = models.TeamClientPermissions()
        self.assertIsInstance(result, models.TeamClientPermissions)

    def test_teamclientpermissions_pickername(self):
        """Test for retreiving pickername on TeamClientPermissions instance"""
        dachshunds = self.fixtures.dachshunds
        team_client_permission = self.fixtures.team_client_permission
        self.assertEqual(team_client_permission.pickername, dachshunds.title)

    def test_teamclientpermissions_userid(self):
        """Test for retreving userid of a TeamClientPermissions instance """
        dachshunds = self.fixtures.dachshunds
        team_client_permission = self.fixtures.team_client_permission
        self.assertEqual(team_client_permission.userid, dachshunds.userid)
