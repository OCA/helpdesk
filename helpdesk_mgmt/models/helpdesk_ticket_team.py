from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

#
# class VIEW(models.Model):
#     _inherit = "ir.ui.view"
#
#     def write(self, vals):
#         import pdb; pdb.set_trace()
#         return super(VIEW, self).write(vals)


class HelpdeskTeam(models.Model):
    _name = "helpdesk.ticket.team"
    _description = "Helpdesk Ticket Team"
    _inherit = ["mail.thread", "mail.alias.mixin"]

    def _compute_endpoint_view_id(self):
        if self.name == "Soporte":
            self.endpoint_view_id = False
            if not self.endpoint_view_id:
                _template = self.env.ref("helpdesk_mgmt.portal_create_ticket")
                xmlid = _template.xml_id + str(self.id)
                form_template = self.env['ir.ui.view'].create({
                    'type': 'qweb',
                    'arch': _template.arch,
                    'name': xmlid,
                    'key': xmlid
                })
                self.env['ir.model.data'].create({
                    'module': 'helpdesk_mgmt',
                    'name': xmlid.split('.')[1],
                    'model': 'ir.ui.view',
                    'res_id': form_template.id,
                    'noupdate': True
                })
                self.write({'endpoint_view_id': form_template.id})


    @api.depends("name", "enable_webform")
    def _compute_endpoint_webform(self, recompute=False):
        """
         Compute the endpoint webform name,
        which usually is the team name hyphen-separated.
        As team names conflicts can exist,
        the endpoint string will be appended the team id to, if necessary
        :return:
        """
        for record in self:
            if (record.enable_webform and not record.endpoint_webform) or recompute:
                _endpoint = "-".join(record.name.lower().split(" "))
                domain = [("endpoint_webform", "=", _endpoint)]
                if isinstance(record.id, int):
                    domain.append(("id", "!=", record.id))
                if record.env[record._name].search(domain):
                    _endpoint += "-{}".format(record.id)
                record.endpoint_webform = _endpoint
                record.endpoint_full_webform = "help/team/{}".format(
                    record.endpoint_webform
                )

    def recompute_endpoint(self):
        self._compute_endpoint_webform(recompute=True)
        self._compute_endpoint_view_id()

    name = fields.Char(string="Name", required=True)
    user_ids = fields.Many2many(comodel_name="res.users", string="Members")
    active = fields.Boolean(default=True)
    category_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.category", string="Category"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one(
        comodel_name="res.users", string="Team Leader", check_company=True,
    )
    alias_id = fields.Many2one(
        comodel_name="mail.alias",
        string="Email",
        ondelete="restrict",
        required=True,
        help="The email address associated with \
                               this channel. New emails received will \
                               automatically create new tickets assigned \
                               to the channel.",
    )
    color = fields.Integer(string="Color Index", default=0)
    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket", inverse_name="team_id", string="Tickets",
    )
    auto_assign_fixed_user_id = fields.Many2one(
        string="Fixed assignment user", comodel_name="res.users"
    )
    auto_assign_type = fields.Selection(
        string="Assignment type",
        selection=[
            ("manual", "Manual"),
            ("random", "Random"),
            ("balanced", "Balanced"),
            ("fixed", "Fixed"),
        ],
        default="manual",
        help="""Random and balanced are both balancing algorithms: `Random`
        will ensure all members have the same number of tickets while `Balanced`
        will assign tickets to the member with the least not closed assigned tickets.
        On the other hand, the `Fixed` selection will ensure the selected member from
        the `Fixed assignment user` field will always be picked as the ticket doer.

         All assignments, be it manual or automatic, will be done with the team's
        defined members on the left of this field
        """,
    )
    todo_ticket_ids = fields.One2many(
        related="ticket_ids",
        domain="[('closed', '=', False)]",
        string="Todo tickets",
        readonly=True,
    )
    todo_ticket_count = fields.Integer(
        string="Number of tickets", compute="_compute_todo_tickets"
    )
    todo_ticket_count_unassigned = fields.Integer(
        string="Number of tickets unassigned", compute="_compute_todo_tickets"
    )
    todo_ticket_count_unattended = fields.Integer(
        string="Number of tickets unattended", compute="_compute_todo_tickets"
    )
    todo_ticket_count_high_priority = fields.Integer(
        string="Number of tickets in high priority", compute="_compute_todo_tickets"
    )
    enable_webform = fields.Boolean(string="Enable team webform")
    endpoint_webform = fields.Char(
        string="Webform endpoint", store=True, compute=_compute_endpoint_webform
    )
    endpoint_full_webform = fields.Char(
        string="Full webform endpoint", store=True, compute=_compute_endpoint_webform
    )
    endpoint_view_id = fields.Many2one(
        comodel_name='ir.ui.view',
        string='Endpoint view')

    @api.onchange("auto_assign_type")
    def _onchange_assign_user_domain(self):
        if self.auto_assign_type == "fixed":
            return {"domain": {"auto_assign_fixed_user_id": [("share", "=", False)]}}

    @api.depends("ticket_ids", "ticket_ids.stage_id")
    def _compute_todo_tickets(self):
        for record in self:
            _todo_ticket_ids = record.todo_ticket_ids.filtered(lambda x: not x.closed)
            record.todo_ticket_count = len(_todo_ticket_ids)
            record.todo_ticket_count_unassigned = len(
                _todo_ticket_ids.filtered(lambda ticket: not ticket.user_id)
            )
            record.todo_ticket_count_unattended = len(
                _todo_ticket_ids.filtered(lambda ticket: ticket.unattended)
            )
            record.todo_ticket_count_high_priority = len(
                _todo_ticket_ids.filtered(lambda ticket: ticket.priority == "3")
            )

    def get_alias_model_name(self, vals):
        return "helpdesk.ticket"

    def get_alias_values(self):
        values = super().get_alias_values()
        values["alias_defaults"] = defaults = safe_eval(self.alias_defaults or "{}")
        defaults["team_id"] = self.id
        return values
