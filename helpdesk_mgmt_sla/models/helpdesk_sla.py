#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class HelpdeskSla(models.Model):
    _name = "helpdesk.sla"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Helpdesk SLA"

    name = fields.Char(required=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    team_ids = fields.Many2many(comodel_name="helpdesk.ticket.team", string="Teams")
    category_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.category", string="Categories"
    )
    tag_ids = fields.Many2many(comodel_name="helpdesk.ticket.tag", string="Tags")
    ignore_stage_ids = fields.Many2many("helpdesk.ticket.stage", string="Ignore Stages")
    stage_id = fields.Many2one("helpdesk.ticket.stage")
    days = fields.Integer(default=0, required=True)
    hours = fields.Integer(default=0, required=True)
    note = fields.Html()
    domain = fields.Char(string="Filter", default="[]")
    active = fields.Boolean(default=True)
