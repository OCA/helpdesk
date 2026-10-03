# Copyright 2024 Nitrokey GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestWebsiteHelpdeskForm(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env["ir.model"].search(
            [("model", "=", "helpdesk.ticket")], limit=1
        )

    def test_model_website_form_access(self):
        """helpdesk.ticket must be enabled for the website form builder."""
        self.assertTrue(
            self.model.website_form_access,
            "helpdesk.ticket must have website_form_access = True",
        )

    def test_model_website_form_key(self):
        """helpdesk.ticket must be registered in the JS FormEditorRegistry."""
        self.assertEqual(
            self.model.website_form_key,
            "create_helpdesk_ticket",
            "helpdesk.ticket must have website_form_key = 'create_helpdesk_ticket'",
        )

    def test_model_website_form_label(self):
        """helpdesk.ticket must have a meaningful form label."""
        self.assertEqual(
            self.model.website_form_label,
            "Create a Ticket",
        )

    def test_whitelisted_fields(self):
        """The expected fields must not be blacklisted for the form builder."""
        expected_fields = {
            "name",
            "description",
            "partner_name",
            "partner_email",
            "category_id",
            "team_id",
        }
        blacklisted_fields = self.env["ir.model.fields"].search(
            [
                ("model_id", "=", self.model.id),
                ("name", "in", list(expected_fields)),
                ("website_form_blacklisted", "=", True),
            ]
        )
        self.assertFalse(
            blacklisted_fields,
            f"The following fields should not be blacklisted: "
            f"{blacklisted_fields.mapped('name')}",
        )
