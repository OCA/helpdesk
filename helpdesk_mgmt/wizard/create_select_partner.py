from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HelpdeskTicketPartner(models.TransientModel):
    _name = "helpdesk.ticket.partner"
    _description = "Create new or use existing Partner on Helpdesk Ticket"

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)

        active_model = self._context.get("active_model")
        if active_model != "helpdesk.ticket":
            raise UserError(_("You can only apply this action from a ticket."))

        ticket = False
        if result.get("ticket_id"):
            ticket = self.env["helpdesk.ticket"].browse(result["ticket_id"])
        elif "ticket_id" in fields and self._context.get("active_id"):
            ticket = self.env["helpdesk.ticket"].browse(self._context["active_id"])
        if ticket:
            result["ticket_id"] = ticket.id
            result["partner_name"] = ticket.partner_name
            result["partner_email"] = ticket.partner_email
            partner_id = result.get("partner_id")
            if "action" in fields and not result.get("action"):
                result["action"] = "exist" if partner_id else "create"
            if "partner_id" in fields and not result.get("partner_id"):
                result["partner_id"] = partner_id

        return result

    action = fields.Selection(
        [
            ("create", "Create a new customer"),
            ("exist", "Link to an existing customer"),
        ],
        string="Quotation Customer",
        required=True,
    )

    @api.model
    def _lang_get(self):
        return self.env["res.lang"].get_installed()

    ticket_id = fields.Many2one("helpdesk.ticket", "Associated Lead", required=True)
    partner_id = fields.Many2one("res.partner", "Customer")
    partner_name = fields.Char(string="Name")
    partner_email = fields.Char(string="Email")
    partner_lang = fields.Selection(selection=_lang_get, string="Language")

    @api.onchange("action", "partner_id")
    def _reset_partner_fields(self):
        if self.action == "create":
            self.partner_name = self.ticket_id.partner_name
            self.partner_email = self.ticket_id.partner_email
            self.partner_lang = self.ticket_id.partner_lang
        else:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email
            self.partner_lang = self.partner_id.lang

    def action_apply(self):
        """Create or select the partner for the ticket and proceed to the email composer"""
        self.ensure_one()
        if self.action == "create":
            self.ticket_id.partner_id = self.env["res.partner"].create(
                {
                    "name": self.partner_name,
                    "email": self.partner_email,
                    "lang": self.partner_lang,
                }
            )
        elif self.action == "exist":
            self.ticket_id.partner_id = self.partner_id
        self.ticket_id._onchange_partner_id()
        return self.ticket_id.action_do_send_email()
