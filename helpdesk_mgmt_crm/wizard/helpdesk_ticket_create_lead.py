# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, api, fields, models


class HelpdeskTicketCreateLead(models.TransientModel):
    _name = "helpdesk.ticket.create.lead"
    _description = "Helpdesk Ticket Create Lead"

    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket",
        required=True,
        readonly=True,
        domain=[("lead_id", "=", False)],
    )
    user_id = fields.Many2one(comodel_name="res.users")
    team_id = fields.Many2one(comodel_name="crm.team")

    @api.model
    def default_get(self, fields):
        vals = super().default_get(fields)
        ticket = self.env["helpdesk.ticket"].browse([self.env.context.get("active_id")])
        if ticket:
            vals.update({"ticket_id": ticket.id})
        return vals

    def _prepare_vals(self):
        return {
            "ticket_id": self.ticket_id.id,
            "name": self.ticket_id.name,
            "partner_id": self.ticket_id.partner_id.id,
            "user_id": self.user_id.id or self.ticket_id.user_id.id,
            "team_id": self.team_id.id,
            "description": self.ticket_id.description,
            "type": "opportunity",
        }

    def action_helpdesk_ticket_to_lead(self):
        lead = self.env["crm.lead"].create(self._prepare_vals())
        for follower in self.ticket_id.message_follower_ids:
            lead.message_subscribe(
                partner_ids=[follower.partner_id.id],
                subtype_ids=follower.subtype_ids.ids,
            )
        self.ticket_id.write({"lead_ids": [(4, lead.id)]})
        for message in self.ticket_id.message_ids:
            message.copy(
                {
                    "model": lead._name,
                    "res_id": lead.id,
                    # prevent null value in column "notification_type" if message
                    # have notifications (not copied)
                    "notified_partner_ids": False,
                }
            )
        # Chatter reflects new Lead
        body = _(
            "This ticket has been converted to the opportunity "
            "<a href=# data-oe-model=%(model)s data-oe-id=%(id)s>%(name)s</a>"
        ) % {"id": lead.id, "name": lead.name, "model": lead._name}
        self.ticket_id.with_user(SUPERUSER_ID).message_post(body=body)
        return lead.get_formview_action()
