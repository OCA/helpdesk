from odoo.tests import Form

from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase


class TestHelpdeskTicket(TestHelpdeskTicketBase):
    def test_helpdesk_ticket_duplicates(self):
        wizard_action = self.ticket_a_unassigned.action_open_duplicate_wizard()
        with Form.from_action(self.env, wizard_action) as wizard:
            wizard.duplicate_of_id = self.ticket_b_unassigned
            wizard_rec = wizard.save()
        wizard_rec.action_confirm()
        self.assertEqual(
            self.ticket_a_unassigned.duplicate_id, self.ticket_b_unassigned
        )
        self.assertIn(self.ticket_b_unassigned.duplicate_ids, self.ticket_a_unassigned)
