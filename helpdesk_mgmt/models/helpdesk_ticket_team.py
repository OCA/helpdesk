from odoo import api, fields, models


class HelpdeskTeam(models.Model):

    _name = 'helpdesk.ticket.team'
    _description = 'Helpdesk Ticket Team'
    _inherit = ['mail.thread', 'mail.alias.mixin']

    name = fields.Char(string='Name', required=True)
    user_ids = fields.Many2many(comodel_name='res.users', string='Members')
    active = fields.Boolean(default=True)
    category_ids = fields.Many2many(
        comodel_name='helpdesk.ticket.category',
        string='Category')
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )
    alias_id = fields.Many2one(help="The email address associated with "
                               "this channel. New emails received will "
                               "automatically create new tickets assigned "
                               "to the channel.")
    color = fields.Integer("Color Index", default=0)

    ticket_ids = fields.One2many(
        'helpdesk.ticket',
        'team_id',
        string="Tickets")

    todo_ticket_ids = fields.One2many(
        'helpdesk.ticket',
        'team_id',
        string="Todo tickets", domain=[("closed", '=', False)])

    todo_ticket_count = fields.Integer(
        string="Number of tickets",
        compute='_compute_todo_tickets')

    todo_ticket_count_unassigned = fields.Integer(
        string="Number of tickets unassigned",
        compute='_compute_todo_tickets')

    todo_ticket_count_unattended = fields.Integer(
        string="Number of tickets unattended",
        compute='_compute_todo_tickets')

    todo_ticket_count_high_priority = fields.Integer(
        string="Number of tickets in high priority",
        compute='_compute_todo_tickets')

    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_todo_tickets(self):
        ticket_model = self.env["helpdesk.ticket"]
        fetch_data = ticket_model.read_group(
            [("team_id", "in", self.ids), ("closed", "=", False)],
            ["team_id", "user_id", "unattended", "priority"],
            ["team_id", "user_id", "unattended", "priority"],
            lazy=False,
        )
        result = [
            [
                data["team_id"][0],
                data["user_id"] and data["user_id"][0],
                data["unattended"],
                data["priority"],
                data["__count"]
            ] for data in fetch_data
        ]
        for team in self:
            team.todo_ticket_count = sum([
                r[4] for r in result
                if r[0] == team.id
            ])
            team.todo_ticket_count_unassigned = sum([
                r[4] for r in result
                if r[0] == team.id and not r[1]
            ])
            team.todo_ticket_count_unattended = sum([
                r[4] for r in result
                if r[0] == team.id and r[2]
            ])
            team.todo_ticket_count_high_priority = sum([
                r[4] for r in result
                if r[0] == team.id and r[3] == "3"
            ])

    def get_alias_model_name(self, vals):
        return 'helpdesk.ticket'

    def get_alias_values(self):
        values = super(HelpdeskTeam, self).get_alias_values()
        values['alias_defaults'] = {'team_id': self.id}
        return values
