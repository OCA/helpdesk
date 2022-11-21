# Copyright 2022 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import users

from . import common

EMPLOYEE = "user_employee"


@tagged("post_install")
class Test(common.TestDS):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls._get_user(
            cls,
            login=EMPLOYEE,
            groups="sales_team.group_sale_salesman_all_leads, helpdesk_mgmt.group_helpdesk_manager",
        )
        helpdesk_ticket_ids, sale_ids = [], []
        for helpdesk_ticket in (
            "ticket 1",
            "ticket 2",
        ):
            helpdesk_ticket_ids.append(
                {"name": helpdesk_ticket, "description": helpdesk_ticket}
            )
        cls.helpdesk_tickets = cls.env["helpdesk.ticket"].create(helpdesk_ticket_ids)
        for sale in ("sale 1", "sale 2", "sale 3"):
            sale_ids.append(
                {"name": sale, "partner_id": cls.env.ref("base.res_partner_2").id}
            )
        cls.sales = cls.env["sale.order"].create(sale_ids)
        cls.sales_helpdesk_ticket_2 = cls.sales.filtered(
            lambda s: s.name in ("sale 2", "sale 3")
        )

        cls.sale_1 = cls.sales.filtered(lambda s: s.name == "sale 1")
        cls.sale_2 = cls.sales.filtered(lambda s: s.name == "sale 2")
        cls.sale_3 = cls.sales.filtered(lambda s: s.name == "sale 3")
        cls.helpdesk_ticket_1 = cls.helpdesk_tickets.filtered(
            lambda s: s.name == "ticket 1"
        )
        cls.helpdesk_ticket_2 = cls.helpdesk_tickets.filtered(
            lambda s: s.name == "ticket 2"
        )

    @users(EMPLOYEE)
    def test_attache_helpdesk_tickets_to_sales(self):
        self.assertEqual(self.helpdesk_ticket_1.sale_ids, self.env["sale.order"])
        self.assertEqual(self.helpdesk_ticket_1.sale_count, 0)
        self.sale_1.helpdesk_ticket_id = self.helpdesk_ticket_1
        self.assertEqual(self.helpdesk_ticket_1.sale_ids, self.sale_1)
        self.assertEqual(self.helpdesk_ticket_1.sale_count, 1)
        self.sale_2.helpdesk_ticket_id = self.helpdesk_ticket_2
        self.sale_3.helpdesk_ticket_id = self.helpdesk_ticket_2
        self.assertEqual(self.helpdesk_ticket_2.sale_count, 2)
        self.assertEqual(self.helpdesk_ticket_2.sale_ids, self.sales_helpdesk_ticket_2)
