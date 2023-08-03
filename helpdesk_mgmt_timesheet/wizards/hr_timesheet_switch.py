# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrTimesheetSwitch(models.TransientModel):
    _inherit = "hr.timesheet.switch"

    @api.model
    def _closest_suggestion(self):
        """Allow searching best suggestion by helpdesk.ticket."""
        result = super()._closest_suggestion()
        if (
            not result
            and self.env.context["active_model"] == "helpdesk.ticket"
            and self.env.user
        ):
            return self.env["account.analytic.line"].search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("ticket_id", "=", self.env.context["active_id"]),
                ],
                order="date_time DESC",
                limit=1,
            )
        return result
