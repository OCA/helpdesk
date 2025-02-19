from odoo import Command, api, fields, models


class HelpdeskTicketMerge(models.TransientModel):
    _name = "helpdesk.ticket.merge"
    _description = "Helpdesk Ticket Merge"

    ticket_ids = fields.Many2many(
        "helpdesk.ticket", string="Tickets to Merge", required=True
    )
    user_id = fields.Many2one("res.users", string="Assigned to")
    create_new_ticket = fields.Boolean(string="Create a new ticket")
    dst_ticket_name = fields.Char(string="New ticket name")
    dst_helpdesk_team_id = fields.Many2one(
        "helpdesk.ticket.team", string="Destination Helpdesk Team"
    )
    dst_ticket_id = fields.Many2one(
        "helpdesk.ticket", string="Merge into an existing ticket"
    )

    def merge_tickets(self):
        tag_ids = self.ticket_ids.mapped("tag_ids").ids
        attachment_ids = self.ticket_ids.mapped("attachment_ids").ids
        user_ids = self.ticket_ids.mapped("user_ids").ids
        values = {
            "tag_ids": [Command.link(tag_id) for tag_id in tag_ids],
            "attachment_ids": [
                Command.link(attachment_id) for attachment_id in attachment_ids
            ],
            "user_ids": [Command.link(user_id) for user_id in user_ids],
        }

        values["user_id"] = self.user_id.id
        if self.create_new_ticket:
            partner_ids = self.ticket_ids.mapped("partner_id")
            ticket_category_ids = self.ticket_ids.mapped("category_id").ids
            priorities = self.ticket_ids.mapped("priority")
            values.update(
                {
                    "name": self.dst_ticket_name,
                    "team_id": self.dst_helpdesk_team_id.id,
                    "description": self._merge_description(self.ticket_ids),
                    "partner_id": len(set(partner_ids)) == 1
                    and partner_ids[0].id
                    or False,
                    "partner_name": len(set(partner_ids)) == 1
                    and partner_ids[0].name
                    or False,
                    "partner_email": len(set(partner_ids)) == 1
                    and partner_ids[0].email
                    or False,
                    "category_id": len(set(ticket_category_ids)) == 1
                    and ticket_category_ids[0]
                    or False,
                    "priority": len(set(priorities)) == 1 and priorities[0] or False,
                }
            )

            self.dst_ticket_id = self.env["helpdesk.ticket"].create(values)
        else:
            values["description"] = "\n".join(
                (
                    self.dst_ticket_id.description or "",
                    self._merge_description(self.ticket_ids - self.dst_ticket_id),
                )
            )
            self.dst_ticket_id.write(values)

        merged_tickets = self.ticket_ids - self.dst_ticket_id
        self._merge_followers(merged_tickets)
        for ticket in merged_tickets:
            self._add_message("to", self.dst_ticket_id.number, ticket)
        ticket_numbers = ", ".join(merged_tickets.mapped("number"))
        self._add_message("from", ticket_numbers, self.dst_ticket_id)
        merged_tickets.write({"active": False})

        return {
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "views": [[False, "form"]],
            "res_id": self.dst_ticket_id.id,
        }

    def _merge_description(self, tickets):
        return "\n".join(
            tickets.mapped(
                lambda ticket: self.env._(
                    "Description from ticket %(name)s: %(description)s"
                )
                % {
                    "name": ticket.name,
                    "description": ticket.description or self.env._("No description"),
                }
            )
        )

    def _merge_followers(self, merged_tickets):
        self.dst_ticket_id.message_subscribe(
            partner_ids=(merged_tickets).mapped("message_partner_ids").ids,
        )

    def default_get(self, fields):
        result = super().default_get(fields)
        selected_tickets = self.env["helpdesk.ticket"].browse(
            self.env.context.get("active_ids", False)
        )
        assigned_tickets = selected_tickets.filtered(lambda ticket: ticket.user_id)
        result.update(
            {
                "ticket_ids": [Command.set(selected_tickets.ids)],
                "user_id": assigned_tickets and assigned_tickets[0].user_id.id or False,
                "dst_helpdesk_team_id": selected_tickets[0].team_id.id,
                "dst_ticket_id": selected_tickets[0].id,
            }
        )
        return result

    @api.onchange("dst_ticket_id")
    def _onchange_dst_ticket_id(self):
        if self.dst_ticket_id.user_id:
            self.user_id = self.dst_ticket_id.user_id

    def _add_message(self, way, ticket_numbers, ticket):
        """Send a message post with to advise the helpdesk ticket about the merge.
        :param way : choice between "from" or "to"
        :param ticket_numbers : list of helpdesk ticket numbers to add in the body
        :param ticket : the ticket where the message will be posted
        """
        subject = "Merge helpdesk ticket"
        body = self.env._(
            f"This helpdesk ticket has been merged {way} {ticket_numbers}"
        )

        ticket.message_post(
            body=body,
            subject=subject,
            message_type="comment",
            subtype_id=self.env.ref("mail.mt_comment").id,
        )
