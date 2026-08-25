# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.addons.base.tests.common import BaseCommon

from ..hooks import uninstall_hook


class TestUninstallHook(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.action = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_dashboard_action")
        cls.partner_kanban_view = cls.env.ref(
            "helpdesk_mgmt_partner_dashboard.helpdesk_ticket_partner_kanban_view"
        )
        cls.partner_tree_view = cls.env.ref(
            "helpdesk_mgmt_partner_dashboard.helpdesk_ticket_partner_tree_view"
        )

    def test_uninstall_hook_restores_original_dashboard_action(self):
        self.assertEqual(self.action.res_model, "res.partner")
        self.assertEqual(
            {view.view_mode: view.view_id for view in self.action.view_ids},
            {"kanban": self.partner_kanban_view, "tree": self.partner_tree_view},
        )

        uninstall_hook(self.env)

        self.assertEqual(self.action.res_model, "helpdesk.ticket.team")
        self.assertEqual(self.action.view_mode, "kanban,tree,form,pivot")
        self.assertFalse(self.action.domain)

    def test_uninstall_hook_missing_action_does_not_raise(self):
        self.action.unlink()

        uninstall_hook(self.env)
