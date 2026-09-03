# Copyright 2022-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from markupsafe import Markup

from odoo import SUPERUSER_ID, _, api, fields, models

# Inline images in a message body are served by id, as /web/image/<id> or
# /web/content/<id>, optionally followed by a filename and a query string.
ATTACHMENT_URL_RE = re.compile(r"/web/(image|content)/(\d+)")


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

    def _copy_message_attachments(self, message, new_message):
        """Give the message copied to the lead its own attachments.

        ``mail.message.attachment_ids`` is a many2many, so copying a message
        leaves the copy pointing at the *same* ``ir.attachment`` records, which
        stay attached to the ticket. An attachment has no access rules of its
        own: reading one checks read access on the record named by its
        ``res_model``/``res_id``. So a salesperson who can see the lead but not
        the ticket gets an ``AccessError`` for every file of the copied
        chatter, which the ``/web/image`` route answers with a placeholder
        image instead of the picture.

        Copy the attachments onto the lead so the copy stands on its own. The
        ticket keeps its originals, and deleting either record no longer takes
        the other one's files with it.
        """
        id_map = {}
        new_attachments = self.env["ir.attachment"]
        for attachment in message.attachment_ids:
            copied = attachment.copy(
                {"res_model": new_message.model, "res_id": new_message.res_id}
            )
            id_map[attachment.id] = copied.id
            new_attachments |= copied
        if not id_map:
            return
        vals = {"attachment_ids": [fields.Command.set(new_attachments.ids)]}
        # Inline images name their attachment by id in the body, so the body
        # has to follow the copies. Their access token is copied along with the
        # attachment, which keeps the rest of the URL valid.
        body = new_message.body or ""
        new_body = ATTACHMENT_URL_RE.sub(
            lambda match: "/web/%s/%s"
            % (match.group(1), id_map.get(int(match.group(2)), match.group(2))),
            body,
        )
        if new_body != body:
            vals["body"] = new_body
        new_message.write(vals)

    def action_helpdesk_ticket_to_lead(self):
        lead = self.env["crm.lead"].create(self._prepare_vals())
        for follower in self.ticket_id.message_follower_ids:
            lead.message_subscribe(
                partner_ids=[follower.partner_id.id],
                subtype_ids=follower.subtype_ids.ids,
            )
        self.ticket_id.write({"lead_ids": [(4, lead.id)]})
        for message in self.ticket_id.message_ids:
            new_message = message.copy(
                {
                    "model": lead._name,
                    "res_id": lead.id,
                    # prevent null value in column "notification_type" if message
                    # have notifications (not copied)
                    "notified_partner_ids": False,
                }
            )
            self._copy_message_attachments(message, new_message)
        # Chatter reflects new Lead
        body = Markup(
            _("This ticket has been converted to the opportunity %(lead_link)s")
        ) % {"lead_link": lead._get_html_link(title=lead.name)}
        self.ticket_id.with_user(SUPERUSER_ID).message_post(body=body)
        return lead.get_formview_action()
