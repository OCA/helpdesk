# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Odoo, Open Source Management Solution
#
#    Author: Andrius Laukavičius. Copyright: JSC NOD Baltic
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp import models, api

class mail_message(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        if vals.get('type') == 'email' and vals.get('model') == 'crm.helpdesk':
            helpdesk_obj = self.env['crm.helpdesk']
            helpdesk = helpdesk_obj.search([('id', '=', vals.get('res_id'))])
            if helpdesk:
                if helpdesk.state in ('done', 'cancel', 'pending'):
                    helpdesk.state = 'open'
        return super(mail_message, self).create(vals)
