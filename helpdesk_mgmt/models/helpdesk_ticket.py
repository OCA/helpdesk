from odoo import _, api, fields, models


class HelpdeskTicket(models.Model):

    _name = 'helpdesk.ticket'
    _rec_name = 'number'
    _order = 'number desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_stage_id(self):
        return self.env['helpdesk.ticket.stage'].search([], limit=1).id

    number = fields.Char(string='Ticket number', default="/",
                         readonly=True)
    name = fields.Char(string='Title', required=True)
    description = fields.Text(required=True)
    user_id = fields.Many2one(
        'res.users',
        string='Assigned user',)
    stage_id = fields.Many2one(
        'helpdesk.ticket.stage',
        string='Stage',
        default=_get_default_stage_id)
    partner_id = fields.Many2one('res.partner')
    partner_name = fields.Char()
    partner_email = fields.Char()

    last_stage_update = fields.Datetime(
        string='Last Stage Update',
        default=fields.Datetime.now(),
    )
    assigned_date = fields.Datetime(string='Assigned Date')
    closed_date = fields.Datetime(string='Closed Date')

    tag_ids = fields.Many2many('helpdesk.ticket.tag')
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )
    channel_id = fields.Many2one(
        'helpdesk.ticket.channel',
        string='Channel',
        help='Channel indicates where the source of a ticket'
             'comes from (it could be a phone call, an email...)',
    )
    category_id = fields.Many2one('helpdesk.ticket.category',
                                  string='Category')
    team_id = fields.Many2one('helpdesk.ticket.team')
    priority = fields.Selection(selection=[
        ('0', _('Low')),
        ('1', _('Medium')),
        ('2', _('High')),
        ('3', _('Very High')),
    ], string='Priority', default='1')
    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id',
        domain=[('res_model', '=', 'website.support.ticket')],
        string="Media Attachments")

    def send_user_mail(self):
        self.env.ref('helpdesk.assignment_email_template').\
            send_mail(self.id)

    @api.model
    def create(self, vals):
        if vals.get('number', '/') == '/':
            vals['number'] = self.env['ir.sequence'].next_by_code(
                'helpdesk.ticket.sequence'
            ) or '/'
        res = super().create(vals)

        # Check if mail to the user has to be sent
        if vals.get('user_id') and res:
            res.send_user_mail()
        return res

    @api.multi
    def write(self, vals):
        for ticket in self:
            now = fields.Datetime.now()
            if vals.get('stage_id'):
                stage_obj = self.env['helpdesk.ticket.stage'].browse(
                    [vals['stage_id']])
                vals['last_stage_update'] = now
                if stage_obj.closed:
                    vals['closed_date'] = now
            if vals.get('user_id'):
                vals['assigned_date'] = now

        res = super(HelpdeskTicket, self).write(vals)

        # Check if mail to the user has to be sent
        for ticket in self:
            if vals.get('user_id'):
                ticket.send_user_mail()
        return res

    def assign_to_me(self):
        self.write({'user_id': self.env.user.id})
