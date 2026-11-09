# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    ticket_id = fields.Many2one("helpdesk.ticket", readonly=True)
    ticket_partner_id = fields.Many2one("res.partner", readonly=True)

    @api.model
    def _select(self):
        return (
            super()._select()
            + """,
            A.ticket_id AS ticket_id,
            A.ticket_partner_id AS ticket_partner_id
        """
        )
