from odoo import fields, models


class HelpdeskTicketInfo(models.Model):
    _name = "helpdesk.ticket"
    _inherit = [_name, "custom.info"]

    custom_info_template_id = fields.Many2one(context={"default_model": _name})
    custom_info_ids = fields.One2many(context={"default_model": _name})
