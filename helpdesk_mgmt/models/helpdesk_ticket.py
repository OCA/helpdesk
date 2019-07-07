from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):

    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _rec_name = 'number'
    _order = 'number desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_stage_id(self):
        return self.env['helpdesk.ticket.stage'].search([], limit=1).id

    number = fields.Char(string='Ticket number', default="/",
                         readonly=True)
    name = fields.Char(string='Title', required=True)
    description = fields.Text()
    closed_description = fields.Text()

    user_id = fields.Many2one(
        'res.users',
        string='Assigned user',help='the user that has/had to solve this ticket')

    user_ids = fields.Many2many(
        comodel_name='res.users',
        related='team_id.user_ids',
        string='Users')


    @api.depends('team_id',)
    def _get_team_id_partners(self):
        for record in self:
            if record.team_id:
                record.user_ids_partner_ids = [x.partner_id.id for x in record.team_id.user_ids]#[(6,0,[x.partner_id.id for x in record.team_id.user_ids])]
            else:
                record.user_ids_partner_ids = False#[(5,0,0)]

    user_ids_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        compute='_get_team_id_partners',
        string='team_id Users partners for sending email with template')
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['helpdesk.ticket.stage'].search([])
        return stage_ids

    stage_id = fields.Many2one(
        'helpdesk.ticket.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
        default=_get_default_stage_id,
        track_visibility='onchange',
    )
    
    def _default_partner_can_not_change(self):
        if not self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user'): 
            return True

    partner_id_can_not_change = fields.Boolean(help='a invisible field just not to let you modify the partner_id ( is readonly based on this field)',default=_default_partner_can_not_change)
    
    def _default_partner_id(self):
        if not self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user'): 
            # user is less than a user that can solve the problem so can not change the partner; the partner is him
            return  self.env.user.partner_id

            
    partner_id = fields.Many2one('res.partner',track_visibility="onchange", default=_default_partner_id, help="the problem/issue/ticket is for this partner")
    partner_name = fields.Char()
    partner_email = fields.Char()

    last_stage_update = fields.Datetime(
        string='Last Stage Update',
        default=fields.Datetime.now(),
    )
    assigned_date = fields.Datetime(string='Assigned Date')
    closed_date = fields.Datetime(string='Closed Date')
    closed = fields.Boolean(related='stage_id.closed')
    unattended = fields.Boolean(related='stage_id.unattended')
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
             'comes from (it could be a phone call, an email...)',default=lambda self: self.env['helpdesk.ticket.channel'].search([('name','ilike','web')],limit=1)
    )
    category_id = fields.Many2one('helpdesk.ticket.category',default=lambda self: self.env['helpdesk.ticket.category'].search([('id','!=',0)],limit=1),
                                  string='Category')
    team_id = fields.Many2one('helpdesk.ticket.team',help='the team that has/had to solve this ticket')
    priority = fields.Selection(selection=[
        ('0', _('Low')),
        ('1', _('Medium')),
        ('2', _('High')),
        ('3', _('Very High')),
    ], string='Priority', default='1')
    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id',
        domain=[('res_model', '=', 'helpdesk.ticket')],
        string="Media Attachments")

    def assign_to_me(self):
        self.write({'user_id': self.env.user.id})

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id:
            self.team_id = self.category_id.team_id
            if self.team_id:
                return {'domain': {'user_id': [('id', 'in', self.user_ids.ids)]}}


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email

    @api.multi
    @api.onchange('team_id', 'user_id')
    def _onchange_dominion_user_id(self):
        if self.user_id:
            if self.user_id and self.user_ids and \
                    self.user_id not in self.user_ids:
                self.update({
                    'user_id': False
                })
                return {'domain': {'user_id': []}}
        if self.team_id:
            return {'domain': {'user_id': [('id', 'in', self.user_ids.ids)]}}
        else:
            return {'domain': {'user_id': []}}

    @api.constrains('team_id','user_id')
    def _check_user_grom_team(self):
        for record in self:
            if record.team_id and record.user_id and record.user_id not in record.team_id.user_ids :
                raise ValidationError(f"User {record.user_id.name} is not member of team {record.team_id.name} ")



    def send_user_mail(self,type):
        if type=='create':
            email_template = self.env.ref('helpdesk_mgmt.assignment_email_template')
        else:
            email_template = self.env.ref('helpdesk_mgmt.closed_email_template')
        email_template.send_mail(self.id)
    
    
    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------

    @api.model
    def create(self, vals):
        if vals.get('number', '/') == '/':
            seq = self.env['ir.sequence']
            if 'company_id' in vals:
                seq = seq.with_context(force_company=vals['company_id'])
            vals['number'] = seq.next_by_code(
                'helpdesk.ticket.sequence') or '/'
        res = super().create(vals)

        # Check if mail to the user has to be sent
        if (vals.get('user_id') or vals.get('team_id')) and res:
            res.send_user_mail('create')  # user_id and team_id notification
        return res

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "number" not in default:
            default['number'] = self.env['ir.sequence'].next_by_code(
                'helpdesk.ticket.sequence'
            ) or '/'
        res = super(HelpdeskTicket, self).copy(default)
        return res

    @api.multi
    def write(self, vals):
        for ticket in self:
            now = fields.Datetime.now()
            if vals.get('stage_id'):
                stage_obj = self.env['helpdesk.ticket.stage'].browse(
                    [vals['stage_id']])  # not the old stage but that after write
                vals['last_stage_update'] = now
                if stage_obj.closed:
                    vals['closed_date'] = now
# and send message to partner that his ticket was closed
                    if  ticket.partner_id :
                        ticket.send_user_mail('close')

            if vals.get('user_id'):
                vals['assigned_date'] = now

        res = super(HelpdeskTicket, self).write(vals)

        # Check if mail to the user has to be sent
#         for ticket in self:
#             if vals.get('user_id') or vals.get('partner_id'):
#                 ticket.send_mail()
        return res

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.multi
    def _track_template(self, tracking):
        "mail if stage_id has a mail_template_id"
        res = super(HelpdeskTicket, self)._track_template(tracking)
        test_task = self[0]
        changes, tracking_value = tracking[test_task.id]
        if "stage_id" in changes and test_task.stage_id.mail_template_id:
            res['stage_id'] = (test_task.stage_id.mail_template_id,
                               {"composition_mode": "mass_mail"})

        return res

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Override message_new from mail gateway so we can set correct
        default values.
        """
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'description': msg.get('body'),
            'partner_email': msg.get('from'),
            'partner_id': msg.get('author_id')
        }
        defaults.update(custom_values)

        # Write default values coming from msg
        ticket = super().message_new(msg, custom_values=defaults)

        # Use mail gateway tools to search for partners to subscribe
        email_list = tools.email_split(
            (msg.get('to') or '') + ',' + (msg.get('cc') or '')
        )
        partner_ids = [p for p in ticket._find_partner_from_emails(
            email_list, force_create=False
        ) if p]
        ticket.message_subscribe(partner_ids)

        return ticket

    @api.multi
    def message_update(self, msg, update_vals=None):
        """ Override message_update to subscribe partners """
        email_list = tools.email_split(
            (msg.get('to') or '') + ',' + (msg.get('cc') or '')
        )
        partner_ids = [p for p in self._find_partner_from_emails(
            email_list, force_create=False
        ) if p]
        self.message_subscribe(partner_ids)
        return super().message_update(msg, update_vals=update_vals)

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super().message_get_suggested_recipients()

        for ticket in self:
            reason = _('Partner Email') \
                if ticket.partner_id and ticket.partner_id.email \
                else _('Partner Id')

            if ticket.partner_id and ticket.partner_id.email:
                ticket._message_add_suggested_recipient(
                    recipients,
                    partner=ticket.partner_id,
                    reason=reason
                )
            elif ticket.partner_email:
                ticket._message_add_suggested_recipient(
                    recipients,
                    email=ticket.partner_email,
                    reason=reason
                )
        return recipients
