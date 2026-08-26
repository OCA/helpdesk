# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _timesheet_determine_sale_line(self):
        if self.ticket_id:
            return self.ticket_id.sale_line_id
        return super()._timesheet_determine_sale_line()
