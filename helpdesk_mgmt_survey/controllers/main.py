import odoo.http as http
from odoo.http import request


class HelpdeskTicketController(http.Controller):

    @http.route('/ticket/survey/<token>',
        type='http', auth='public', website=True)
    def ticket_survey(self, token):
        """Display Survey"""
        ticket = request.env['helpdesk.ticket'].sudo(). \
            search([('access_token', '=', token)])

        ticket.no_score = False
        ticket.comment = ''
        if ticket.rating:
            return http.request.render( \
                'helpdesk_survey.survey_already_complete', {
                    "ticket": ticket})
        else:
            return http.request.render( \
                'helpdesk_survey.helpdesk_ticket_survey_page', {
                    "ticket": ticket})

    @http.route('/ticket/survey/completed/<token>',
        type='http', auth='public', website=True)
    def survey_completed(self, token, **kw):
        """Update ticket with survey response"""

        ticket = request.env['helpdesk.ticket'].sudo(). \
            search([('access_token', '=', token)])

        vals = {}

        for field_name, field_value in kw.items():
            vals[field_name] = field_value

        if 'support_rating' not in vals:
            ticket.no_score = True
            if vals.get('comment'):
                ticket.comment = vals.get('comment')
            else:
                ticket.comment = ''
            return http.request.render(
                'helpdesk_survey.helpdesk_ticket_survey_page', {
                    'ticket': ticket})

        ticket.rating = vals['support_rating']
        ticket.comment = vals['comment']
        ticket.survey_done = True

        return http.request.render('helpdesk_survey.survey_completed_page', {
            "ticket": ticket})
