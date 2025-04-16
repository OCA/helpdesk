# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.addons.base.tests.common import BaseCommon


class TestHelpdeskCategoryHierarchy(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_1 = cls.env["helpdesk.ticket.category"].create({"name": "C1"})
        cls.category_2 = cls.env["helpdesk.ticket.category"].create(
            {"name": "C2", "parent_id": cls.category_1.id}
        )

    def test_helpdesk_ticket_category(self):
        self.assertEqual(self.category_2.complete_name, "C1 / C2")
