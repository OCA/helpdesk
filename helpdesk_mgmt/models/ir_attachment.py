from odoo import models, api


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def check(self, mode, values=None):
        group_portal = self.env.ref('base.group_portal')
        if (
            mode == 'write' and values.get('res_model') == 'helpdesk.ticket' and
            group_portal.id in self.env.user.groups_id.ids
        ):
            # when portal user is writing a file attached to a ticket,
            # skip access check to ticket, allowing to write
            # (needed for example by website_portal_comment_attachment)
            del values['res_model']
        return super(Attachment, self).check(mode, values)
