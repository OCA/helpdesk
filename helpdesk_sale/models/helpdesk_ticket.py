# Copyright (C) 2020 Callino
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.depends('order_ids')
    def _compute_sale_order_count(self):
        for ticket in self:
            ticket.sale_order_count = len(ticket.order_ids)

    order_ids = fields.One2many('sale.order', 'ticket_id', string='Linked orders')
    sale_order_count = fields.Integer('Order Count', compute='_compute_sale_order_count', store=True)

    def create_order(self):
        self.ensure_one()
        action = self.env.ref('sale.action_quotations').read()[0]
        ref = self.env.ref('sale.view_order_form')
        action['views'] = [(ref.id, 'form')]
        action['context'] = {
            'default_ticket_id': self.id,
            'default_partner_id': self.partner_id.commercial_partner_id.id,
        }
        return action

    def open_orders(self):
        self.ensure_one()
        action = self.env.ref('sale.action_quotations').read()[0]
        action['context'] = {
            'default_ticket_id': self.id,
            'default_partner_id': self.partner_id.commercial_partner_id.id,
        }
        action['domain'] = [('ticket_id', '=', self.id)]
        return action

