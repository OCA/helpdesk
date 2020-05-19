###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
import logging
from odoo.tests.common import TransactionCase
from odoo import fields

_log = logging.getLogger(__name__)


class TestHelpdeskTicket(TransactionCase):

    def setUp(self):
        super().setUp()
        self.account_id = self.env['account'].create({
            'name': 'Test Account',
        })

    def generate_timesheet(self, hours=1.0):
        return self.env['account.analytic.line'].create({
            'account_id': self.account_id.id,
            'amount': 0,
            'company_id': 1,
            'date': fields.Date.today(),
            'name': 'Test Timesheet',
            'unit_amount': hours,
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
