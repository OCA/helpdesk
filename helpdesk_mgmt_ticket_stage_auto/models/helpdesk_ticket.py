from odoo import models
import datetime


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def auto_stage_tickets(self):

        auto_stage = self.sudo().search([("stage_id.auto_stage", "=", True)])
        for ticket in auto_stage:
            interval_number = ticket.stage_id.inactivity_time
            stage_days = datetime.timedelta(days=interval_number)
            date_stage = datetime.datetime.now()
            if (ticket.last_timesheet_activity):
                last_timesheet = datetime.datetime.combine(
                    ticket.last_timesheet_activity,
                    datetime.time(date_stage.hour, date_stage.minute)
                )
                last_update = max(ticket.last_stage_update,
                                  last_timesheet)
            else:
                last_update = ticket.last_stage_update
            last_update = last_update + stage_days

            if last_update <= date_stage:
                stage_ticket = ticket.stage_id.destination_stage.id
                ticket.write({
                    "stage_id": stage_ticket
                })
