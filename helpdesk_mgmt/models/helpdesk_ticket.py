from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "Helpdesk Ticket"
    _rec_name = "number"
    _order = "number desc"
    _mail_post_access = "read"
    _inherit = ["portal.mixin", "mail.thread.cc", "mail.activity.mixin"]

    def _get_default_stage_id(self):
        return self.env["helpdesk.ticket.stage"].search([], limit=1).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env["helpdesk.ticket.stage"].search([])
        return stage_ids

    number = fields.Char(string="Ticket number", default="/", readonly=True)
    name = fields.Char(string="Title", required=True)
    description = fields.Html(required=True, sanitize_style=True)
    user_id = fields.Many2one(comodel_name="res.users", string="Assigned user")
    user_ids = fields.Many2many(
        comodel_name="res.users", related="team_id.user_ids", string="Users"
    )
    stage_id = fields.Many2one(
        comodel_name="helpdesk.ticket.stage",
        string="Stage",
        group_expand="_read_group_stage_ids",
        default=_get_default_stage_id,
        tracking=True,
        ondelete="restrict",
        index=True,
        copy=False,
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Contact")
    partner_name = fields.Char()
    partner_email = fields.Char(string="Email")

    last_stage_update = fields.Datetime(
        string="Last Stage Update", default=fields.Datetime.now
    )
    assigned_date = fields.Datetime(string="Assigned Date")
    closed_date = fields.Datetime(string="Closed Date")
    closed = fields.Boolean(related="stage_id.closed")
    unattended = fields.Boolean(related="stage_id.unattended", store=True)
    tag_ids = fields.Many2many(comodel_name="helpdesk.ticket.tag", string="Tags")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    channel_id = fields.Many2one(
        comodel_name="helpdesk.ticket.channel",
        string="Channel",
        help="Channel indicates where the source of a ticket"
        "comes from (it could be a phone call, an email...)",
    )
    category_id = fields.Many2one(
        comodel_name="helpdesk.ticket.category",
        string="Category",
    )
    team_id = fields.Many2one(
        comodel_name="helpdesk.ticket.team",
        string="Team",
    )
    priority = fields.Selection(
        selection=[
            ("0", "Low"),
            ("1", "Medium"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        string="Priority",
        default="1",
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        domain=[("res_model", "=", "helpdesk.ticket")],
        string="Media Attachments",
    )
    color = fields.Integer(string="Color Index")
    kanban_state = fields.Selection(
        selection=[
            ("normal", "Default"),
            ("done", "Ready for next stage"),
            ("blocked", "Blocked"),
        ],
        string="Kanban State",
    )
    active = fields.Boolean(default=True)

    def send_user_mail(self):
        self.send_message(
            self.env.ref("helpdesk_mgmt.assignment_email_template"),
            notif_layout="mail.mail_notification_paynow",
        )

    def assign_to_me(self):
        self.write({"user_id": self.env.user.id})

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email

    @api.onchange("team_id", "user_id")
    def _onchange_dominion_user_id(self):
        if self.user_id and self.user_ids and self.user_id not in self.team_id.user_ids:
            self.update({"user_id": False})
            return {"domain": {"user_id": []}}
        if self.team_id:
            return {"domain": {"user_id": [("id", "in", self.user_ids.ids)]}}
        else:
            return {"domain": {"user_id": []}}

    def _compute_access_url(self):
        super(HelpdeskTicket, self)._compute_access_url()
        for ticket in self:
            ticket.access_url = "/my/ticket/%s" % ticket.id

    def send_message(
        self,
        template,
        lang=False,
        subtype_id=False,
        force_send=True,
        composition_mode="comment",
        notif_layout=None,
        system_author=False,
    ):
        """This method sends ticket communication by email, using a template given
        as a parameter.

         :param template: a mail.template record used to compute the message body;
         :param lang: optional lang; it can also be specified directly on the
         templateitself in the lang field;
         :param subtype_id: optional subtype to use when creating the message; it
         is a note by default to avoid spamming followers;
         :param force_send: whether to send the request directly or use the mail
         queue cron (preferred option);
         :param composition_mode: comment (message_post) or mass_mail (template.send_mail);
         :param notif_layout: layout used to encapsulate the content when sending email;
         :param system_author: send the message as if from the system root user
        """
        if lang:
            template = template.with_context(lang=lang)
        if subtype_id is False:
            subtype_id = self.env["ir.model.data"].xmlid_to_res_id("mail.mt_note")
        if force_send:
            self = self.with_context(mail_notify_force_send=True)
        for record in self:
            if system_author:
                record = record.with_user(self.env.ref("base.user_root")).sudo()
            record.message_post_with_template(
                template.id,
                composition_mode=composition_mode,
                email_layout_xmlid=notif_layout
                if notif_layout is not None
                else "mail.mail_notification_light",
                subtype_id=subtype_id,
            )

    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------

    @api.model
    def create(self, vals):
        if vals.get("number", "/") == "/":
            vals["number"] = self._prepare_ticket_number(vals)
        res = super().create(vals)

        # Check if mail to the user has to be sent
        if vals.get("user_id") and res:
            res.send_user_mail()
        return res

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "number" not in default:
            default["number"] = self._prepare_ticket_number(default)
        res = super().copy(default)
        return res

    def write(self, vals):
        for _ticket in self:
            now = fields.Datetime.now()
            if vals.get("stage_id"):
                stage = self.env["helpdesk.ticket.stage"].browse([vals["stage_id"]])
                vals["last_stage_update"] = now
                if stage.closed:
                    vals["closed_date"] = now
            if vals.get("user_id"):
                vals["assigned_date"] = now

        res = super().write(vals)

        # Check if mail to the user has to be sent
        for ticket in self:
            if vals.get("user_id"):
                ticket.send_user_mail()
        return res

    def action_duplicate_tickets(self):
        for ticket in self.browse(self.env.context["active_ids"]):
            ticket.copy()

    def _prepare_ticket_number(self, values):
        seq = self.env["ir.sequence"]
        if "company_id" in values:
            seq = seq.with_company(values["company_id"])
        return seq.next_by_code("helpdesk.ticket.sequence") or "/"

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    def _track_template(self, tracking):
        res = super()._track_template(tracking)
        ticket = self[0]
        if "stage_id" in tracking and ticket.stage_id.mail_template_id:
            res["stage_id"] = (
                ticket.stage_id.mail_template_id,
                {
                    "auto_delete_message": True,
                    "subtype_id": self.env["ir.model.data"].xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                    "email_layout_xmlid": "mail.mail_notification_paynow",
                },
            )
        return res

    @api.model
    def message_new(self, msg, custom_values=None):
        """Override message_new from mail gateway so we can set correct
        default values.
        """
        if custom_values is None:
            custom_values = {}
        defaults = {
            "name": msg.get("subject") or _("No Subject"),
            "description": msg.get("body"),
            "partner_email": msg.get("from"),
            "partner_id": msg.get("author_id"),
            "channel_id": self.env.ref(
                "helpdesk_mgmt.helpdesk_ticket_channel_email"
            ).id,
        }
        defaults.update(custom_values)

        # Write default values coming from msg
        ticket = super().message_new(msg, custom_values=defaults)

        if ticket.partner_id:
            # If we have a partner trigger the partner onchange function
            ticket._onchange_partner_id()

            # Send acknowledgement email only if we have a partner. We don't
            # want to send a response to just any address that sends us an
            # email. Send the message as the system user because Odoo won't
            # send an email to the author of a message.
            ticket.send_message(
                self.env.ref("helpdesk_mgmt.new_ticket_template"),
                notif_layout="mail.mail_notification_paynow",
                system_author=True,
            )

        # Use mail gateway tools to search for partners to subscribe
        email_list = tools.email_split(
            (msg.get("to") or "") + "," + (msg.get("cc") or "")
        )
        partner_ids = [
            p
            for p in self.env["mail.thread"]._mail_find_partner_from_emails(
                email_list, records=ticket, force_create=False
            )
            if p
        ]
        ticket.message_subscribe(partner_ids)

        return ticket

    def message_update(self, msg, update_vals=None):
        """ Override message_update to subscribe partners """
        email_list = tools.email_split(
            (msg.get("to") or "") + "," + (msg.get("cc") or "")
        )
        partner_ids = [
            p
            for p in self.env["mail.thread"]._mail_find_partner_from_emails(
                email_list, records=self, force_create=False
            )
            if p
        ]
        self.message_subscribe(partner_ids)
        return super().message_update(msg, update_vals=update_vals)

    def _message_get_suggested_recipients(self):
        recipients = super()._message_get_suggested_recipients()
        try:
            for ticket in self:
                if ticket.partner_id:
                    ticket._message_add_suggested_recipient(
                        recipients, partner=ticket.partner_id, reason=_("Customer")
                    )
                elif ticket.partner_email:
                    ticket._message_add_suggested_recipient(
                        recipients,
                        email=ticket.partner_email,
                        reason=_("Customer Email"),
                    )
        except AccessError:
            # no read access rights -> just ignore suggested recipients because this
            # imply modifying followers
            pass
        return recipients
