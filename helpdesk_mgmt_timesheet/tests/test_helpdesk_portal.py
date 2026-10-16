# Copyright 2023 DEC (https://www.decgroupe.com)
# Copyright 2026 Mario Castillo López <@mcastillol14>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_portal


class TestHelpdeskPortal(test_helpdesk_portal.TestHelpdeskPortalBase):
    def setUp(self):
        super().setUp()
        self.env.company.helpdesk_mgmt_portal_select_team = True

    def test_submit_ticket_team(self):
        # helpdesk_mgmt.helpdesk_team_2 is demo data, not loaded by default since 19.0
        team_id = self.env["helpdesk.ticket.team"].create({"name": "Test Team"})
        self.authenticate("portal", "portal")
        self._submit_ticket(team=team_id.id)
        tickets = self.get_new_tickets(self.user_portal)
        self.assertIn(self.portal_ticket, tickets)
        self.assertIn(team_id, tickets.mapped("team_id"))

    # portal submission has no project field, it must be taken from the team
    def test_submit_ticket_team_fills_default_project(self):
        project = self.env["project.project"].create({"name": "Team default project"})
        team_id = self.env["helpdesk.ticket.team"].create(
            {"name": "Test Team With Project", "default_project_id": project.id}
        )
        self.authenticate("portal", "portal")
        self._submit_ticket(team=team_id.id)
        tickets = self.get_new_tickets(self.user_portal)
        new_ticket = tickets.filtered(lambda t: t.team_id == team_id)
        self.assertEqual(new_ticket.project_id, project)
