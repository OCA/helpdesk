# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSuggestedRecipientsTour(HttpCase):
    def test_helpdesk_recipient_unchecked(self):
        admin_user = self.env.ref("base.user_admin")
        company = admin_user.company_id

        partner = (
            self.env["res.partner"]
            .with_company(company)
            .create(
                {
                    "name": "Test Contact Uncheck Partner",
                    "email": "test.contact@example.com",
                }
            )
        )

        self.env["helpdesk.ticket"].with_company(company).create(
            {
                "name": "Test Contact Uncheck",
                "partner_id": partner.id,
                "user_id": admin_user.id,
                "description": "Description Test",
            }
        )

        self.start_tour(
            "/odoo/my-helpdesk-tickets?view_type=list",
            "helpdesk_suggested_recipient_tour",
            login="admin",
        )
