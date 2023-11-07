from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    helpdesk_ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="partner_id",
        string="Related tickets",
    )

    helpdesk_ticket_count = fields.Integer(
        compute="_compute_helpdesk_ticket_count", string="Ticket count"
    )

    helpdesk_ticket_active_count = fields.Integer(
        compute="_compute_helpdesk_ticket_count", string="Ticket active count"
    )

    helpdesk_ticket_count_string = fields.Char(
        compute="_compute_helpdesk_ticket_count", string="Tickets"
    )

    def _compute_helpdesk_ticket_count(self):
        ticket_data = self.env["helpdesk.ticket"].read_group(
            [("partner_id", "child_of", self.ids)], ["partner_id"], ["partner_id"]
        )
        active_ticket_data = self.env["helpdesk.ticket"].read_group(
            [("partner_id", "child_of", self.ids), ("stage_id.closed", "=", False)],
            ["partner_id"],
            ["partner_id"],
        )
        mapped_data = {x["partner_id"][0]: x["partner_id_count"] for x in ticket_data}
        active_mapped_data = {
            x["partner_id"][0]: x["partner_id_count"] for x in active_ticket_data
        }
        for record in self:
            record.helpdesk_ticket_count = mapped_data.get(record.id, 0)
            record.helpdesk_ticket_active_count = active_mapped_data.get(record.id, 0)
            for child in record.child_ids:
                record.helpdesk_ticket_count += mapped_data.get(child.id, 0)
                record.helpdesk_ticket_active_count += active_mapped_data.get(
                    child.id, 0
                )
            count_active = record.helpdesk_ticket_active_count
            count = record.helpdesk_ticket_count
            record.helpdesk_ticket_count_string = "{} / {}".format(count_active, count)

    def action_view_helpdesk_tickets(self):
        return {
            "name": self.name,
            "view_mode": "tree,form",
            "res_model": "helpdesk.ticket",
            "type": "ir.actions.act_window",
            "domain": [("partner_id", "child_of", self.id)],
            "context": self.env.context,
        }
