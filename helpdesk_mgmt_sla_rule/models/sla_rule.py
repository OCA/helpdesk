# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SlaRule(models.Model):
    _name = "sla.rule"
    _description = "SLA Rule"
    _order = "sequence asc"

    name = fields.Char(string="Name", help="Name of the SLA Rule.", required=True)
    sequence = fields.Integer(
        string="Sequence", help="Sequence number of the SLA rule."
    )
    team_id = fields.Many2one(
        "helpdesk.ticket.team", string="Team", help="Team of the SLA Rule."
    )
    stage_id = fields.Many2one(
        "helpdesk.ticket.stage", string="Stage", help="Stage of the SLA Rule."
    )
    category_id = fields.Many2one(
        "helpdesk.ticket.category", string="Category", help="Category of the SLA Rule."
    )
    match_categ = fields.Boolean(
        string="Match Category", help="Match category of the SLA Rule."
    )
    tag_ids = fields.Many2many(
        "helpdesk.ticket.tag", string="Tags", help="Tags of the SLA Rule."
    )
    match_tags = fields.Selection(
        [("all", "All"), ("any", "Any"), ("none", "None")],
        string="Match Tags",
        help="Match tags of the SLA Rule.",
    )
    type_id = fields.Many2one(
        "helpdesk.ticket.type", string="Type", help="Type of the SLA Rule."
    )
    match_type = fields.Boolean(string="Match Type", help="Match type of the SLA Rule.")
    sla_id = fields.Many2one(
        "helpdesk.sla", string="SLA", help="SLA of the SLA Rule.", required=True
    )
