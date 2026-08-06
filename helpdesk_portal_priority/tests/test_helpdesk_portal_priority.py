from odoo.tests.common import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserPortal


@tagged("post_install", "-at_install")
class TestHelpdeskPortalPriority(HttpCaseWithUserPortal):
    def test_new_ticket_form_has_priority_selector(self):
        self.authenticate("portal", "portal")
        resp = self.url_open("/new/ticket")
        self.assertEqual(resp.status_code, 200)
        self.assertIn('name="priority"', resp.text)
