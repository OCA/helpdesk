from odoo import models, fields


class HelpdeskTicketStage(models.Model):
    _inherit = 'helpdesk.ticket.stage'

    rating_mail_template_id = fields.Many2one(
        'mail.template',
        string="Rating Email Template",
        domain=[('model', '=', 'helpdesk.ticket')],
        help="If set, an email will be sent to the customer  "
             "with a rating survey when the ticket reaches this stage.")
