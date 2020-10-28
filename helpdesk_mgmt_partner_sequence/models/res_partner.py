from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    helpdesk_ticket_sequence_id = fields.Many2one(
        'ir.sequence', string='Helpdesk Ticket Sequence',
        help="This field contains the information related to "
             "the numbering of the tickets of this partner.",
        copy=False)
    helpdesk_ticket_sequence_number_next = fields.Integer(
        string='Helpdesk Ticket Next Number',
        help='The next sequence number will be used '
             'for the next ticket of this partner.',
        compute='_compute_seq_helpdesk_ticket_number_next',
        inverse='_inverse_seq_helpdesk_ticket_number_next')

    @api.multi
    @api.depends('helpdesk_ticket_sequence_id.use_date_range',
                 'helpdesk_ticket_sequence_id.number_next_actual')
    def _compute_seq_helpdesk_ticket_number_next(self):
        '''Compute 'helpdesk_ticket_sequence_number_next'
        according to the current sequence in use,
        an ir.sequence or an ir.sequence.date_range.
        '''
        for p in self:
            if p.helpdesk_ticket_sequence_id:
                seq = p.helpdesk_ticket_sequence_id._get_current_sequence()
                p.helpdesk_ticket_sequence_number_next = seq.number_next_actual
            else:
                p.helpdesk_ticket_sequence_number_next = None

    @api.multi
    def _inverse_seq_helpdesk_ticket_number_next(self):
        '''Inverse 'helpdesk_ticket_sequence_number_next'
        to edit the current sequence next number.
        '''
        for p in self:
            if p.helpdesk_ticket_sequence_id:
                if p.helpdesk_ticket_sequence_number_next:
                    seq = p.helpdesk_ticket_sequence_id._get_current_sequence()
                    seq.sudo().number_next = \
                        p.helpdesk_ticket_sequence_number_next
