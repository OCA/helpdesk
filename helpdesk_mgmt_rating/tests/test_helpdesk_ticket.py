# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged
from odoo import _


@tagged("post_install", "-at_install")
class TestHelpDeskTicket(TransactionCase):
    def setUp(self):
        super(TestHelpDeskTicket, self).setUp()
        self.partner = self.env.ref("base.res_partner_1")
        self.template = self.env["mail.template"].create(
            {
                "name": "Rating Email Template",
                "model_id": self.env["ir.model"]
                .search([("model", "=", "helpdesk.ticket")])
                .id,
            }
        )
        self.ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Helpdesk Ticket",
                "description": "Test Helpdesk Ticket",
                "partner_id": self.partner.id,
            }
        )

    def test_compute_percentage(self):
        self.ticket.rating_ids = []
        self.ticket._compute_percentage()
        self.assertEqual(self.ticket.positive_rate_percentage, -1)

    def test_write(self):
        stage_initial = self.env["helpdesk.ticket.stage"].create(
            {
                "name": "Initial Stage",
            }
        )
        self.ticket.stage_id = stage_initial
        stage_rating = self.env["helpdesk.ticket.stage"].create(
            {
                "name": "Rating Stage",
                "rating_mail_template_id": self.template.id,
            }
        )
        self.ticket.write({"stage_id": stage_rating.id})
        self.assertTrue(self.ticket.stage_id.rating_mail_template_id)
        self.assertTrue(self.ticket._send_ticket_rating_mail)

    def test_send_ticket_rating_mail(self):
        self.ticket.write(
            {
                "rating_status": "stage_change",
            }
        )
        self.assertEqual(self.ticket.rating_status, "stage_change")
        stage_rating = self.env["helpdesk.ticket.stage"].create(
            {
                "name": "Rating Stage",
                "rating_mail_template_id": self.template.id,
            }
        )
        survey_template = stage_rating.rating_mail_template_id
        self.assertTrue(survey_template)
        self.ticket.rating_send_request(
            survey_template,
            lang=self.ticket.partner_id.lang,
            force_send=False,
        )

    def test_rating_get_partner_id(self):
        partner_id = self.ticket.rating_get_partner_id()
        self.assertEqual(partner_id, self.ticket.partner_id)
        self.ticket.partner_id = False
        partner_id = self.ticket.rating_get_partner_id()
        self.assertFalse(partner_id)
        self.ticket.unlink()

    def test_rating_get_parent_model_name(self):
        model_name = self.ticket.rating_get_parent_model_name(vals={})
        self.assertEquals(model_name, "helpdesk.ticket")

    def test_rating_get_ticket_id(self):
        ticket_id = self.ticket.rating_get_ticket_id()
        self.assertEquals(ticket_id, self.ticket.id)
