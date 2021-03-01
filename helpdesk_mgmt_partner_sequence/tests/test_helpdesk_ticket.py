from odoo.tests import common


class TestHelpdeskTicket(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicket, cls).setUpClass()
        cls.user_admin = cls.env.ref('base.user_root')
        cls.company_1 = cls.env.ref('base.main_company')
        cls.company_2 = cls.env['res.company'].create({
            'name': 'company 2',
        })
        cls.partner_sequence = cls.env['ir.sequence'].create({
            'name': 'Helpdesk partner sequence',
            'prefix': 'HPS',
            'padding': 5,
            'company_id': cls.company_1.id,
        })
        cls.address_sequence = cls.env['ir.sequence'].create({
            'name': 'Helpdesk address sequence',
            'prefix': 'HAS',
            'padding': 5,
            'company_id': cls.company_1.id,
        })
        cls.test_partner = cls.env['res.partner'].create({
            'name': 'Solvos',
            'is_company': True,
            'street': '30 García Barbón',
            'city': 'Vigo',
            'zip': '36201',
            'country_id': cls.env.ref('base.es').id,
            'helpdesk_ticket_sequence_id': cls.partner_sequence.id,
        })
        cls.test_addr_1 = cls.env['res.partner'].create({
            'name': 'Fiscal address',
            'parent_id': cls.test_partner.id,
        })
        cls.test_addr_2 = cls.env['res.partner'].create({
            'name': 'Social address',
            'parent_id': cls.test_partner.id,
            'helpdesk_ticket_sequence_id': cls.address_sequence.id,
        })

    def test_helpdesk_ticket_number(self):
        new_ticket_1 = self.env['helpdesk.ticket'].create({
            'name': 'Test 1',
            'description': 'Ticket test 1',
            'partner_id': self.test_partner.id,
        })
        self.assertEqual(new_ticket_1.number,
                         'HPS00001',
                         'Helpdesk Ticket: When create a test_partner ticket '
                         'the number must be HPS00001.')
        new_ticket_2 = self.env['helpdesk.ticket'].create({
            'name': 'Test 2',
            'description': 'Ticket test 2',
            'partner_id': self.test_addr_1.id,
        })
        self.assertEqual(new_ticket_2.number,
                         'HPS00002',
                         'Helpdesk Ticket: When create a test_addr_1 ticket '
                         'the number must be HPS00002.')
        new_ticket_3 = self.env['helpdesk.ticket'].create({
            'name': 'Test 3',
            'description': 'Ticket test 3',
            'partner_id': self.test_addr_2.id,
        })
        self.assertEqual(new_ticket_3.number,
                         'HAS00001',
                         'Helpdesk Ticket: When create a test_addr_2 ticket '
                         'the number must be HAS00001.')
        new_ticket_4 = self.env['helpdesk.ticket'].create({
            'name': 'Test 4',
            'description': 'Ticket test 4',
        })
        self.assertNotEqual(new_ticket_4.number[0:3],
                            'HPS',
                            'Helpdesk Ticket: When create a no partner ticket '
                            'the ticket number does not prefix HPS.')
        new_ticket_5 = self.env['helpdesk.ticket'].create({
            'name': 'Test 5',
            'description': 'Ticket test 5',
            'partner_id': self.test_addr_2.id,
            'company_id': self.company_2.id,
        })
        self.assertEqual(new_ticket_5.number[0:2],
                         'HT',
                         'Helpdesk Ticket: When create a test_addr_2 ticket '
                         'with other company the ticket number must be HTxxx.')
        self.partner_sequence.write({
            'number_next': 6,
        })
        self.assertEqual(self.test_partner.helpdesk_ticket_sequence_number_next,
                         6,
                         'Helpdesk Sequence: When write number_next in '
                         'partner_sequence must be change in test_partner the '
                         'helpdesk_ticket_sequence_number_next too.')
        self.test_partner.write({
            'helpdesk_ticket_sequence_number_next': 7,
        })
        self.assertEqual(self.partner_sequence.number_next,
                         7,
                         'Partner Sequence: When write sequence_number_next in '
                         'test_partner must be change in partner_sequence the '
                         'number_next too.')
        self.test_addr_2.write({
            'helpdesk_ticket_sequence_id': None,
        })
        self.assertEqual(self.test_addr_2.helpdesk_ticket_sequence_number_next,
                         0,
                         'Partner Sequence: When helpdesk_ticket_sequence_id '
                         'is removed must be removed sequence_number_next too.')
