from odoo import _, api, models, tools


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    @api.model
    def default_get(self, fields):
        result = super(MailComposer, self).default_get(fields)
        if result.get(
            "model", self._context.get("default_model", "")
        ) == "helpdesk.ticket" and result.get("res_id"):
            helpdesk_ticket = self.env["helpdesk.ticket"].browse(
                int(result.get("res_id"))
            )

            if (
                helpdesk_ticket.team_id
                and helpdesk_ticket.team_id.alias_id
                and helpdesk_ticket.team_id.alias_name
                and helpdesk_ticket.team_id.alias_domain
            ):
                result["email_from"] = (
                    helpdesk_ticket.team_id.alias_name
                    + "@"
                    + helpdesk_ticket.team_id.alias_domain
                )

            doc_name_get = helpdesk_ticket.name_get()
            record_name = doc_name_get and doc_name_get[0][1] or ""
            subject = tools.ustr(record_name)

            re_prefix = _("Re:")
            if (
                subject
                and helpdesk_ticket.name not in subject
                and not (subject.startswith("Re:") or subject.startswith(re_prefix))
            ):
                subject = "%s [%s] %s" % (re_prefix, subject, helpdesk_ticket.name)
            elif subject and not (
                subject.startswith("Re:") or subject.startswith(re_prefix)
            ):
                subject = "%s %s" % (re_prefix, subject)
            result["subject"] = subject
        return result
