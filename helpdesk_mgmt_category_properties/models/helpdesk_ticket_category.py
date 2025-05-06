from odoo import fields, models


class HelpdeskCategory(models.Model):
    _inherit = "helpdesk.ticket.category"

    ticket_properties_definition = fields.PropertiesDefinition("Ticket Properties")
