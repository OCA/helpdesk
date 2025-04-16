from odoo import api, fields, models


class HelpdeskCategory(models.Model):
    _name = "helpdesk.ticket.category"
    _description = "Helpdesk Ticket Category"
    _order = "sequence, id"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = "name"
    _rec_name = "complete_name"

    sequence = fields.Integer(default=10)
    active = fields.Boolean(
        default=True,
    )
    name = fields.Char(
        required=True,
        translate=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    parent_id = fields.Many2one(
        "helpdesk.ticket.category",
        "Parent Category",
        index=True,
        ondelete="cascade",
    )
    child_id = fields.One2many(
        "helpdesk.ticket.category", "parent_id", "Child Categories"
    )
    parent_path = fields.Char(index=True)
    complete_name = fields.Char(
        compute="_compute_complete_name", store=True, recursive=True
    )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = (
                    f"{category.parent_id.complete_name} / {category.name}"
                )
            else:
                category.complete_name = category.name
