from odoo import models


class MailMessage(models.Model):
    _inherit = "mail.message"

    def _notify_compute_recipients(self, record, msg_vals):
        recipient_data = super(MailMessage, self)._notify_compute_recipients(
            record, msg_vals
        )
        if self._context.get("skip_follower_recipient"):
            msg_sudo = self.sudo()
            pids = (
                [x[1] for x in msg_vals.get("partner_ids")]
                if "partner_ids" in msg_vals
                else msg_sudo.partner_ids.ids
            )
            new_recipient_partners = []
            for partner_data in recipient_data.get("partners", []):
                if partner_data.get("id") in pids:
                    new_recipient_partners.append(partner_data)

            recipient_data["partners"] = new_recipient_partners

        return recipient_data
