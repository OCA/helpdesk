from odoo import fields, models


class HelpdeskCategory(models.Model):
    _inherit = "helpdesk.ticket.category"

    _parent_name = 'parent_id'
    _parent_store = False

    parent_id = fields.Many2one(
        string= "Parent",
        comodel_name='helpdesk.ticket.category',
        index=True,
        ondelete='cascade'
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        string="Sub-types",
        comodel_name='helpdesk.ticket.category',
        inverse_name='parent_id',
    )

    