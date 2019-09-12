from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    link_docs = fields.Boolean(
        string='Link Documents',
        default=False)

    related_models = fields.Many2many(
        comodel_name='res.request.link',
        string='Select Models')

    @api.onchange('link_docs')
    def _onchange_link_docs(self):
        if not self.link_docs:
            self.related_models = []
            # tickets = self.env['helpdesk.ticket'].search([(
            #     'link_docs', '!=', False)])
            # for ticket in tickets:
            #     ticket.link_docs = False

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', 'link_docs', self.link_docs)
        IrDefault.set('res.config.settings', 'related_models',
                      self.related_models.ids)
        return True

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update({
            'link_docs': IrDefault.get('res.config.settings', 'link_docs'),
            'related_models': IrDefault.get(
                'res.config.settings', 'related_models'),
        })
        return res
