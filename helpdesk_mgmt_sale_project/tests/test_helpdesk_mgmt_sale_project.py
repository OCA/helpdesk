# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestHelpdeskTicketSaleProject(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.project1 = cls.env["project.project"].create({"name": "Project 1"})
        cls.project2 = cls.env["project.project"].create({"name": "Project 2"})
        cls.sale_order1 = cls.env["sale.order"].create(
            {"partner_id": cls.partner.id, "project_id": cls.project1.id}
        )
        cls.sale_order2 = cls.env["sale.order"].create(
            {"partner_id": cls.partner.id, "project_id": cls.project2.id}
        )
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {"name": "Ticket", "description": "Ticket Description"}
        )

    def test_helpdesk_ticket_compute_project_id(self):
        self.ticket.sale_order_ids = [Command.set([self.sale_order1.id])]
        self.assertEqual(self.ticket.project_id, self.project1)

    def test_helpdesk_ticket_check_unique_project(self):
        with self.assertRaises(ValidationError) as error:
            self.ticket.sale_order_ids = [
                Command.set([self.sale_order1.id, self.sale_order2.id])
            ]
        self.assertEqual(
            error.exception.args[0],
            "Ticket 'Ticket' cannot have multiple different projects.",
        )
        self.assertFalse(self.ticket.project_id)
