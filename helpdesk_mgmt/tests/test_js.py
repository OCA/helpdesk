# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import odoo

from odoo.addons.web.tests.test_js import WebSuite


@odoo.tests.tagged("post_install", "-at_install")
class TestHelpdesMgmtJs(WebSuite):
    """Test Automation OCA"""

    def get_hoot_filters(self):
        self._test_params = [("+", "@helpdesk_mgmt")]
        return super().get_hoot_filters()

    def test_helpdesk_mgmt(self):
        self.test_unit_desktop()
