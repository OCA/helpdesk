from odoo.tests import common


class TestHelpdeskTicket(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicket, cls).setUpClass()
        helpdesk_ticket = cls.env['helpdesk.ticket']
        cls.user_admin = cls.env.ref('base.user_root')
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.stage_closed = cls.env.ref('helpdesk.helpdesk_ticket_stage_done')

        cls.ticket = helpdesk_ticket.create({
            'name': 'Test 1',
            'description': 'Ticket test',
        })

    def test_helpdesk_ticket_datetimes(self):
        old_stage_update = self.ticket.last_stage_update

        self.assertTrue(self.ticket.last_stage_update,
                        'Helpdesk Ticket: Helpdesk ticket should '
                        'have a last_stage_update at all times.')

        self.assertFalse(self.ticket.closed_date,
                         'Helpdesk Ticket: No closed date '
                         'should be set for a non closed '
                         'ticket.')

        self.ticket.write({
            'stage_id': self.stage_closed.id,
        })

        self.assertTrue(self.ticket.closed_date,
                        'Helpdesk Ticket: A closed ticket '
                        'should have a closed_date value.')
        self.assertTrue(old_stage_update < self.ticket.last_stage_update,
                        'Helpdesk Ticket: The last_stage_update '
                        'should be updated at every stage_id '
                        'change.')

        self.ticket.write({
            'user_id': self.user_admin.id,
        })
        self.assertTrue(self.ticket.assigned_date,
                        'Helpdesk Ticket: An assigned ticket '
                        'should contain a assigned_date.')

    def test_helpdesk_ticket_number(self):
        self.assertNotEquals(self.ticket.number, '/',
                             'Helpdesk Ticket: A ticket should have '
                             'a number.')
