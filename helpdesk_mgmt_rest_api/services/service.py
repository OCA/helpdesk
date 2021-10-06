# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import AbstractComponent


class BaseHelpdeskService(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "base.helpdesk.rest.service"
    _collection = "helpdesk.rest.services"
    _expose_model = None

    def _get(self, _id):
        return self.env[self._expose_model].browse(_id)
