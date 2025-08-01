# Copyright 2025 Kencove (https://www.kencove.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def _track_template(self, tracking):
        if self.env.context.get("tracking_disable"):
            return dict()
        return super()._track_template(tracking=tracking)
