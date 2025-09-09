from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    former_user_id = fields.Many2one("res.users", string="Former Assignee")

    @api.model
    def _send_assign_email(self, partner, ticket, template_xmlid):
        template = self.env.ref(template_xmlid)
        if template:
            template.sudo().send_mail(
                ticket.id,
                email_values={"recipient_ids": [(6, 0, [partner.id])]},
                force_send=True,
            )

    def write(self, vals):
        old_assign = {rec.id: rec.user_id for rec in self}
        res = super().write(vals)
        if "user_id" in vals:
            for rec in self:
                old_user = old_assign[rec.id]
                new_user = rec.user_id
                current_user = self.env.user
                # Prévenir le nouvel assigné sauf si c'est l'utilisateur actif
                rec.write({"former_user_id": old_user.id})
                if new_user and new_user != current_user:
                    self._send_assign_email(
                        new_user.partner_id,
                        rec,
                        "helpdesk_mgmt_notify_user.mail_template_new_assign",
                    )
                # Prévenir l'ancien assigné sauf si c'est l'utilisateur actif
                if old_user and old_user != current_user and old_user != new_user:
                    self._send_assign_email(
                        old_user.partner_id,
                        rec,
                        "helpdesk_mgmt_notify_user.mail_template_old_assign",
                    )
        return res
