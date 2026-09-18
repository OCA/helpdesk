# Copyright 2023 DEC (https://www.decgroupe.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_portal


class TestHelpdeskPortal(test_helpdesk_portal.TestHelpdeskPortalBase):
    """ """

    def setUp(self):
        super().setUp()
        self.env.company.helpdesk_mgmt_portal_select_team = True

    def test_submit_ticket_team(self):
        team_id = self.env.ref("helpdesk_mgmt.helpdesk_team_2")
        self.authenticate("portal", "portal")
        self._submit_ticket(team=team_id.id)
        tickets = self.get_new_tickets(self.user_portal)
        self.assertIn(self.portal_ticket, tickets)
        self.assertIn(team_id, tickets.mapped("team_id"))
