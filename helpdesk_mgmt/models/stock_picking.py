from odoo import fields, models

class Picking(models.Model):
    _inherit = "stock.picking"

    ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Ticket")
