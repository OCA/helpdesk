from odoo import fields, models, api
from odoo.addons.http_routing.models.ir_http import slugify


class HelpdeskCategory(models.Model):
    _inherit = "helpdesk.ticket.category"
    _rec_name = 'complete_name'

    _parent_store = True
    _parent_name = 'parent_id'

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

    complete_name = fields.Char(
        string = 'Complete Name', 
        compute='_compute_complete_name', 
        store=True
    )

    code = fields.Char(
        string="Code",
        compute="_compute_code",
        readonly=False,
        inverse="_inverse_code",
        store=True,
        index=True
    )

    #
    # Copute fields

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for r in self:
            if r.parent_id:
                r.complete_name = '%s / %s' % (r.parent_id.complete_name, r.name)
            else:
                r.complete_name = r.name

    @api.depends("parent_id", "name", "code")
    def _compute_code(self):
        for r in self:
            if r.name and r.name.strip():
                parent_code = f"{r.parent_id.code}-" if r.parent_id else ""
                r.code = "{}{}".format(parent_code, slugify(r.name))
            else:
                r.code = ""

    def _inverse_code(self):
        for r in self:
            r.code = slugify(r.code)