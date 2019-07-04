from odoo import models, fields, api, _
import uuid


class HelpdeskTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    @api.model
    def _get_access_token(self):
        return str(uuid.uuid4())

    rating = fields.Integer(string="Ticket Rating")
    survey_url = fields.Char(
        compute="_compute_survey_url", string="Survey URL")
    comment = fields.Char(string="Ticket Comment")
    access_token = fields.Char(
        'Security Token', copy=False,
        default=_get_access_token
    )
    survey_done = fields.Boolean('Survey Done', default=False)

    survey_sent = fields.Boolean(
        string='Survey Sent',
        default=False)

    no_score = fields.Boolean(
        default=False)

    @api.one
    def _compute_survey_url(self):
        self.survey_url = "/ticket/survey/" + str(self.access_token)

    @api.multi
    def send_survey(self):
        self.env.ref('helpdesk_survey.survey_email_template'). \
            send_mail(self.id)
        self.survey_sent = True
