# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from typing import List

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.ticket import HelpdeskTicketInfo, HelpdeskTicketRequest

_logger = logging.getLogger(__name__)


class TicketService(Component):
    """Service to manage helpdesk tickets."""

    _name = "helpdesk.ticket.service"
    _inherit = [
        "base.helpdesk.rest.service",
        "mail.thread.abstract.service",
        "abstract.attachable.service",
    ]
    _usage = "helpdesk_ticket"
    _expose_model = "helpdesk.ticket"
    _description = __doc__

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @restapi.method(
        routes=[(["/<int:id>"], "GET")],
        input_param={},
        output_param=PydanticModel(HelpdeskTicketInfo),
    )
    def get(self, _id):
        record = self._get(_id)
        return HelpdeskTicketInfo.from_orm(record)

    @restapi.method(
        routes=[(["/"], "GET")],
        input_param={},
        output_param=PydanticModelList(HelpdeskTicketInfo),
    )
    def search(self):
        domain = self._get_base_search_domain()
        result: List[HelpdeskTicketInfo] = []
        for item in self.env[self._expose_model].search(domain):
            result.append(HelpdeskTicketInfo.from_orm(item))
        return result

    @restapi.method(
        routes=[(["/create"], "POST")],
        input_param=PydanticModel(HelpdeskTicketRequest),
        output_param=PydanticModel(HelpdeskTicketInfo),
    )
    # pylint: disable=W8106
    def create(self, ticket: HelpdeskTicketRequest) -> HelpdeskTicketInfo:
        vals = self._prepare_params(ticket.dict(), mode="create")
        record = self.env[self._expose_model].create(vals)
        return HelpdeskTicketInfo.from_orm(record)

    @restapi.method(
        routes=[(["/<int:id>"], "DELETE")],
        output_param={},
    )
    def cancel(self, _id):
        stage_cancelled = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_cancelled")
        record = self._get(_id)
        record.stage_id = stage_cancelled
        return self.env.datamodels["empty.output"].load({})

    def _params_to_prepare_by_appending_id(self):
        return ["category", "team"]

    def _prepare_params(self, params, mode="create"):
        if mode == "create":
            if params.get("partner"):
                partner = params.pop("partner")
                params["partner_name"] = partner.pop("name")
                params["partner_email"] = partner.pop("email")
                if "lang" in partner:
                    params["partner_lang"] = partner.pop("lang")

            elif self.env.context.get("authenticated_partner_id"):
                params["partner_id"] = self.env.context.get("authenticated_partner_id")
                params.pop("partner", None)
            else:
                raise UserError(_("The partner is mandatory"))

        for key in self._params_to_prepare_by_appending_id():
            val = params.pop(key)
            if val and "id" in val:
                params["%s_id" % key] = val["id"]
        return params

    def _get_base_search_domain(self):
        res = super()._get_base_search_domain()
        res += [("partner_id", "=", self.env.context.get("authenticated_partner_id"))]
        return res
