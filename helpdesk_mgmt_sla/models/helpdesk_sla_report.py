# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskSlaReport(models.Model):
    _name = "helpdesk.sla.report"
    _description = "Helpdesk SLA Report"
    _auto = False

    ticket_id = fields.Many2one("helpdesk.ticket", readonly=True)
    name = fields.Char(readonly=True)
    date = fields.Datetime(readonly=True)
    team_id = fields.Many2one("helpdesk.ticket.team", readonly=True)
    partner_id = fields.Many2one(
        "res.partner", related="ticket_id.partner_id", readonly=True
    )
    state = fields.Selection(
        [
            ("on_going", "Ongoing"),
            ("expired", "Expired"),
            ("accomplished", "Accomplished"),
        ],
    )
    active = fields.Boolean()

    def _where_sla(self):
        return "1=1"

    def _from_sla(self):
        return """
        helpdesk_ticket ht
        JOIN helpdesk_ticket_sla hts ON hts.ticket_id = ht.id
        """

    def _select_sla(self):
        return """
            hts.id as id,
            hts.ticket_id as ticket_id,
            ht.name as name,
            ht.create_date as date,
            ht.team_id as team_id,
            ht.active as active,
            CASE
                WHEN hts.state = 'accomplished' THEN 'accomplished'
                WHEN hts.state = 'expired' OR
                    (hts.state = 'in_progress' and hts.deadline < NOW())
                    THEN 'expired'
                ELSE 'on_going'
            END as state
            """

    def _query(self):
        return f"""
            SELECT {self._select_sla()}
            FROM {self._from_sla()}
            WHERE {self._where_sla()}
        """

    @property
    def _table_query(self):
        return self._query()
