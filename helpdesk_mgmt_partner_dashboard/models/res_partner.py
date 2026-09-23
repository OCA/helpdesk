# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    todo_ticket_count = fields.Integer(
        string="Number of tickets",
        compute="_compute_todo_tickets",
        search="_search_todo_ticket_count",
        recursive=True,
    )
    todo_ticket_count_unassigned = fields.Integer(
        string="Number of tickets unassigned",
        compute="_compute_todo_tickets",
        recursive=True,
    )
    todo_ticket_count_unattended = fields.Integer(
        string="Number of tickets unattended",
        compute="_compute_todo_tickets",
        recursive=True,
    )
    todo_ticket_count_high_priority = fields.Integer(
        string="Number of tickets in high priority",
        compute="_compute_todo_tickets",
        recursive=True,
    )

    @api.depends(
        "helpdesk_ticket_ids.closed",
        "helpdesk_ticket_ids.user_id",
        "helpdesk_ticket_ids.unattended",
        "helpdesk_ticket_ids.priority",
        "child_ids.todo_ticket_count",
        "child_ids.todo_ticket_count_unassigned",
        "child_ids.todo_ticket_count_unattended",
        "child_ids.todo_ticket_count_high_priority",
    )
    def _compute_todo_tickets(self):
        for partner in self:
            own_tickets = partner.helpdesk_ticket_ids.filtered(
                lambda ticket: not ticket.closed
            )
            partner.todo_ticket_count = len(own_tickets) + sum(
                partner.child_ids.mapped("todo_ticket_count")
            )
            partner.todo_ticket_count_unassigned = len(
                own_tickets.filtered(lambda ticket: not ticket.user_id)
            ) + sum(partner.child_ids.mapped("todo_ticket_count_unassigned"))
            partner.todo_ticket_count_unattended = len(
                own_tickets.filtered(lambda ticket: ticket.unattended)
            ) + sum(partner.child_ids.mapped("todo_ticket_count_unattended"))
            partner.todo_ticket_count_high_priority = len(
                own_tickets.filtered(lambda ticket: ticket.priority == "3")
            ) + sum(partner.child_ids.mapped("todo_ticket_count_high_priority"))

    def _search_todo_ticket_count(self, operator, value):
        if operator != "=" or not isinstance(value, bool):
            raise ValueError("Unsupported search operator")
        open_tickets = self.env["helpdesk.ticket"].search(
            [("partner_id", "!=", False), ("closed", "=", False)]
        )
        ancestor_ids = set()
        for partner in open_tickets.partner_id:
            node = partner
            while node:
                ancestor_ids.add(node.id)
                node = node.parent_id
        if value:
            return [("id", "in", list(ancestor_ids))]
        else:
            return [("id", "not in", list(ancestor_ids))]
