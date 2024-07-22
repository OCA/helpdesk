from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_view_helpdesk_tickets(self):
        if self.env.user.has_group(
            "fieldservice.group_fsm_user_own"
        ) and self.env.user.has_group("helpdesk_mgmt.group_helpdesk_user_own"):
            context = dict(self.env.context)
            context.pop("search_default_open", None)
            self = self.with_context(
                context,
                default_partner_id=self.id,
                default_fsm_location_id=self.service_location_id.id,
            )
            return super(ResPartner, self).action_view_helpdesk_tickets()
        return super().action_view_helpdesk_tickets
