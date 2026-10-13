from odoo import api, models
from odoo.osv.expression import AND


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        if not self.env.su and self.env.user.has_group("base.group_portal"):
            partner = self.env.user.partner_id.sudo()
            if partner.helpdesk_team_ids:
                domain = AND(
                    [domain, [("team_id", "in", partner.helpdesk_team_ids.ids)]]
                )
            if partner.helpdesk_category_ids:
                domain = AND(
                    [domain, [("category_id", "in", partner.helpdesk_category_ids.ids)]]
                )
        return super()._search(domain, offset=offset, limit=limit, order=order)
