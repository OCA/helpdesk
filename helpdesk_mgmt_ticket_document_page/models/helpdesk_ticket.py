# Copyright 2025 Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class HelpdeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    document_page_id = fields.Many2one(
        string="Document Page",
        comodel_name="document.page",
        help="Document Page used to attend and handle this ticket",
        tracking=True,
    )

    def action_open_document_page(self):
        """Open the document page associated with the ticket."""
        self.ensure_one()
        if not self.document_page_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Document Page"),
            "res_model": "document.page",
            "res_id": self.document_page_id.id,
            "view_mode": "form",
            "target": "current",
        }
