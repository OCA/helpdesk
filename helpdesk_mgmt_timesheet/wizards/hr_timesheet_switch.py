# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class HrTimesheetSwitch(models.TransientModel):
    _inherit = "hr.timesheet.switch"

    @api.model
    def _closest_suggestion(self):
        """Allow searching best suggestion by helpdesk.ticket."""
        result = super()._closest_suggestion()
        try:
            if not result and self.env.context["active_model"] == "helpdesk.ticket":
                return self.env["account.analytic.line"].search(
                    [
                        ("user_id", "=", self.env.user.id),
                        ("ticket_id", "=", self.env.context["active_id"]),
                    ],
                    order="date_time DESC",
                    limit=1,
                )
        except KeyError:
            # If I don't know where's the user, I don't know what to suggest
            _logger.info("No user found")
        return result
