# coding: utf-8
# Author: Andrius Laukavičius. Copyright: JSC Boolit
# Copyright 2019 Coop IT Easy SCRLfs
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        if vals.get('message_type') != 'notification' and vals.get('model') == 'helpdesk.ticket':
            ticket = self.env["helpdesk.ticket"].search([('id', '=', vals.get('res_id'))])
            if ticket:
                if ticket.stage_id.is_close:
                    stage = self.env["helpdesk.stage"].search([("sequence", "=", 0)])
                    ticket.stage_id = stage
        return super(MailMessage, self).create(vals)
