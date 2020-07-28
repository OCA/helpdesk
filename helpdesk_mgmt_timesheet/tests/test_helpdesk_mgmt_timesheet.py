###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
import logging
from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_ticket
from odoo import fields

_log = logging.getLogger(__name__)


class TestHelpdeskMgmtTimesheet(test_helpdesk_ticket.TestHelpdeskTicket):

    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskMgmtTimesheet, cls).setUpClass()
        cls.project_id = cls.env['project.project'].create({
            'name': 'Project',
        })
        cls.team_id = cls.env['helpdesk.ticket.team'].create({
            'name': "Team 1",
            'allow_timesheet': True,
            'default_project_id': cls.project_id.id,
        })

    def generate_timesheet(self, ticket, hours=1.0):
        return self.env['account.analytic.line'].create({
            'amount': 0,
            'date': fields.Date.today(),
            'name': 'Test Timesheet',
            'unit_amount': hours,
            'ticket_id': ticket.id,
            'project_id': ticket.project_id.id,
        })

    def generate_ticket(self):
        return self.env['helpdesk.ticket'].create({
            'name': 'Test Ticket 1',
            'description': 'Test ticket description',
            'team_id': self.team_id.id,
        })

    def test_helpdesk_mgmt_timesheet(self):
        ticket = self.generate_ticket()
        ticket._onchange_team_id()
        self.assertEqual(
            ticket.project_id.id, self.team_id.default_project_id.id)
        ticket.planned_hours = 5
        timesheet1 = self.generate_timesheet(ticket, 2)
        timesheet2 = self.generate_timesheet(ticket, 1)
        self.assertEqual(
            ticket.total_hours,
            timesheet1.unit_amount + timesheet2.unit_amount)
        self.assertEqual(
            ticket.remaining_hours,
            ticket.planned_hours - ticket.total_hours)
