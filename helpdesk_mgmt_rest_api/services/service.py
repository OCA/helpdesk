# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _
from odoo.exceptions import AccessError, MissingError
from odoo.osv import expression

from odoo.addons.component.core import AbstractComponent
from odoo.addons.datamodel.core import Datamodel


class EmptyOutput(Datamodel):
    _name = "empty.output"


class BaseHelpdeskService(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "base.helpdesk.rest.service"
    _collection = "helpdesk.rest.services"
    _expose_model = None

    def _prepare_params(self, params, mode="create"):
        return params

    def _to_json(self, record, many=False):
        result = record.jsonify(self._json_parser())
        if many:
            return result
        else:
            return result[0]

    def _get(self, _id):
        domain = expression.normalize_domain(self._get_base_search_domain())
        domain = expression.AND([domain, [("id", "=", _id)]])
        record = self.env[self._expose_model].search(domain)
        if not record:
            raise MissingError(
                _("The record %s %s does not exist") % (self._expose_model, _id)
            )
        else:
            return record

    def _get_base_search_domain(self):
        if not self.env.context.get("authenticated_partner_id"):
            raise AccessError(
                _("You should be connected to search for Helpdesk Tickets")
            )
        return []

    def _return_record(self, record):
        return self.env.datamodels["{}.output".format(self._expose_model)].load(
            self._to_json(record)
        )
