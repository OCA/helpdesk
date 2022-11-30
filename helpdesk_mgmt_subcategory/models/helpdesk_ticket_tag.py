from odoo import fields, models


class HelpdeskTicketTag(models.Model):
    _inherit = "helpdesk.ticket.tag"

    tickets_count = fields.Integer(
        string="# Open Tickets", compute="_compute_tickets_count"
    )

    _compute_tickets_count_sql_all = """SELECT helpdesk_ticket_tag_id , COUNT(*)
        FROM helpdesk_ticket_helpdesk_ticket_tag_rel
        WHERE helpdesk_ticket_tag_id in %s
        GROUP BY helpdesk_ticket_tag_id
        """
    _compute_tickets_count_sql_open = """SELECT helpdesk_ticket_tag_id , COUNT(*)
    FROM helpdesk_ticket_helpdesk_ticket_tag_rel t2tt
    LEFT JOIN helpdesk_ticket t ON t.id = t2tt.helpdesk_ticket_id
    WHERE t2tt.helpdesk_ticket_tag_id in %s
    and t.stage_id not in (select id from helpdesk_ticket_stage where closed=true)
    GROUP BY helpdesk_ticket_tag_id
    """

    def _compute_tickets_count(self):
        tag_tickets_count = {}
        if self.ids:
            self.env.cr.execute(
                self._compute_tickets_count_sql_open,
                (tuple(self.ids),),
            )
            tag_tickets_count = dict(self.env.cr.fetchall())
        for r in self:
            r.tickets_count = tag_tickets_count.get(r.id, 0)
