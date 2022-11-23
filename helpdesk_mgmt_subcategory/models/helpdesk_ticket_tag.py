from odoo import fields, models


class HelpdeskTicketTag(models.Model):
    _inherit = "helpdesk.ticket.tag"

    tickets_count = fields.Integer(string="# Tickets", compute="_compute_tickets_count")

    def _compute_tickets_count(self):
        tag_tickets_count = {}
        if self.ids:
            self.env.cr.execute(
                """SELECT helpdesk_ticket_tag_id , COUNT(*)
                FROM helpdesk_ticket_helpdesk_ticket_tag_rel
                WHERE helpdesk_ticket_tag_id in %s
                GROUP BY helpdesk_ticket_tag_id
                """,
                (tuple(self.ids),),
            )
            tag_tickets_count = dict(self.env.cr.fetchall())
        for r in self:
            r.tickets_count = tag_tickets_count.get(r.id, 0)
