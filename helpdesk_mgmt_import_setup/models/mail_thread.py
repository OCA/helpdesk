# Copyright 2025 Kencove (https://www.kencove.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def unlink(self):
        """Preserve mail.message, mail.followers & attachments of helpdesk.ticket
        if skip_remove_mail_message_and_followers is in context."""
        if (
            self.env.context.get("skip_remove_mail_message_and_followers")
            and self._name == "helpdesk.ticket"
        ):
            _logger.info("Preserving mail threads with context")
            placeholder_model = "archive.helpdesk"
            ticket_ids = self.ids
            MailMessage = self.env["mail.message"].sudo()
            MailFollower = self.env["mail.followers"].sudo()

            # Preserve Mail Messages
            messages = MailMessage.search(
                [("model", "=", self._name), ("res_id", "in", ticket_ids)]
            )
            if messages:
                # Preserve attachments
                _logger.info(
                    "Preserving 'mail.message' when uninstalling helpdesk module"
                )
                attachments = messages.mapped("attachment_ids").sudo()
                if attachments:
                    _logger.info(
                        "Preserving 'ir.attachment' when uninstalling helpdesk module"
                    )
                    for att in attachments:
                        att.write(
                            {"res_model": placeholder_model, "old_res_id": att.res_id}
                        )
                    _logger.info(
                        "Preserved %s ir.attachment records",
                        len(attachments),
                    )
                for msg in messages:
                    msg.write({"model": placeholder_model, "old_res_id": msg.res_id})
                _logger.info(
                    "Preserved %s mail.message records",
                    len(messages),
                )
            # Preserve Followers
            followers = MailFollower.search(
                [("res_model", "=", self._name), ("res_id", "in", ticket_ids)]
            )
            if followers:
                for fol in followers:
                    fol.write(
                        {"res_model": placeholder_model, "old_res_id": fol.res_id}
                    )
                _logger.info("Preserved %s mail.followers", len(followers))
            return True
        return super().unlink()


class MailMessage(models.Model):
    _inherit = "mail.message"

    old_res_id = fields.Integer(index=True)


class MailFollower(models.Model):
    _inherit = "mail.followers"

    old_res_id = fields.Integer(index=True)


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    old_res_id = fields.Integer(index=True)
