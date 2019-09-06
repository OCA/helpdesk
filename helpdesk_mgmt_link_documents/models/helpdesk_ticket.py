from odoo import models, fields, api


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    link_settings = fields.Boolean(
        compute='_get_configuration')

    link_docs = fields.Reference(
        string='Related Document',
        selection='get_referencable_models')

    def _get_configuration(self):
        for record in self:
            irDefault = record.env['ir.default'].sudo()
            record.link_settings = irDefault.get('res.config.settings', 'link_docs')

    @api.model
    def get_referencable_models(self):
        irDefault = self.env['ir.default'].sudo()
        ids = irDefault.get('res.config.settings', 'related_models')
        models = self.env['res.request.link'].search(
            [('id', 'in', ids)]
        )
        return[(x.object, x.name) for x in models]

    @api.model
    def default_get(self, fields):
        res = super(HelpdeskTicket, self).default_get(fields)
        irDefault = self.env['ir.default'].sudo()
        link_settings = irDefault.get('res.config.settings', 'link_docs')
        res['link_settings'] = link_settings
        return res
