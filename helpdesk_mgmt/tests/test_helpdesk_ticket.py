from odoo.tests import common


class TestHelpdeskTicket(common.SavepointCase):

    def setUp(self):
        super().setUp()
        self.user_admin = self.env.ref('base.user_root')
        self.user_demo = self.env.ref('base.user_demo')
        self.stage_closed = self.env.ref('helpdesk.helpdesk_ticket_stage_done')

    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicket, cls).setUpClass()
        Ticket = cls.env['helpdesk.ticket']
        cls.ticket = Ticket.create({
            'name': 'Test 1',
            'description': "This is the first test.",
        })

    def test_helpdesk_ticket(self):
        self.assertTrue(self.ticket.last_stage_update)

        self.ticket.write({
            'stage_id': self.stage_closed.id,
        })
        self.assertTrue(self.ticket.closed_date)

        self.ticket.write({
            'user_id': self.user_admin.id,
        })
        self.assertTrue(self.ticket.assigned_date)
