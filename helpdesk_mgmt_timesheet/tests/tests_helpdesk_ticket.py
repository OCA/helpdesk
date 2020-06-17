###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
import logging
from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_ticket
from odoo import fields

_log = logging.getLogger(__name__)


class TestHelpdeskTicketProject(test_helpdesk_ticket.TestHelpdeskTicket):

    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicketProject, cls).setUpClass()
        cls.account_id = cls.env['account.analytic.account'].create({
            'name': 'Test Account',
        })
        cls.team_id = cls.env['helpdesk.ticket.team'].create({
            'name': "Team 1",
            'allow_timesheet': True,
            'default_analytic_account': cls.account_id.id,
        })

    def generate_timesheet(self, hours=1.0):
        return self.env['account.analytic.line'].create({
            'amount': 0,
            'company_id': 1,
            'date': fields.Date.today(),
            'name': 'Test Timesheet',
            'unit_amount': hours,
        })

    def generate_ticket(self):
        return self.env['helpdesk.ticket'].create({
            'name': 'Test Ticket 1',
            'team_id': self.team_id.id,
        })

    def test_total_and_remaining_hours(self):
        ticket = self.generate_ticket()
        ticket.planned_hours = 5
        timesheet1 = self.generate_timesheet(2)
        timesheet1.ticket_id = ticket.id
        timesheet2 = self.generate_timesheet(1)
        timesheet2.ticket_id = ticket.id
        self.assertEqual(ticket.total_hours, 3)
        self.assertEqual(ticket.remaining_hours, 2)
