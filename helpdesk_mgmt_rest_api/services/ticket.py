# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel

_logger = logging.getLogger(__name__)


class HelpdeskPartnerInput(Datamodel):
    _name = "helpdesk.partner.input"

    email = fields.Email(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)


class HelpdeskTeamInput(Datamodel):
    _name = "helpdesk.team.input"

    id = fields.Integer(required=True, allow_none=False)


class HelpdeskTeamOutput(Datamodel):
    _name = "helpdesk.team.output"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)


class HelpdeskCategoryInput(Datamodel):
    _name = "helpdesk.category.input"

    id = fields.Integer(required=True, allow_none=False)


class HelpdeskCategoryOutput(Datamodel):
    _name = "helpdesk.category.output"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)


class HelpdeskStageOutput(Datamodel):
    _name = "helpdesk.stage.output"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)


class HelpdeskTicketBase(Datamodel):
    _name = "helpdesk.ticket.base"

    id = fields.Integer(required=False, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    description = fields.String(required=True, allow_none=False)


class HelpdeskTicketInput(Datamodel):
    _name = "helpdesk.ticket.input"
    _inherit = ["helpdesk.ticket.base"]

    partner = fields.NestedModel(
        "helpdesk.partner.input", required=False, allow_none=False
    )
    category = fields.NestedModel(
        "helpdesk.category.input", required=False, allow_none=False
    )
    team = fields.NestedModel("helpdesk.team.input", required=False, allow_none=False)


class HelpdeskTicketOutput(Datamodel):
    _name = "helpdesk.ticket.output"
    _inherit = ["helpdesk.ticket.base", "mail.thread.output", "attachable.output"]

    create_date = fields.DateTime(required=True, allow_none=False)
    last_stage_update = fields.DateTime(required=True, allow_none=True)
    category = fields.NestedModel(
        "helpdesk.category.output", required=False, allow_none=True
    )
    team = fields.NestedModel("helpdesk.team.output", required=False, allow_none=True)
    stage = fields.NestedModel("helpdesk.stage.output", required=True, allow_none=False)


class HelpdeskTicketSearchOutput(Datamodel):
    _name = "helpdesk.ticket.search.output"

    size = fields.Integer(required=True, allow_none=False)
    data = fields.NestedModel(
        "helpdesk.ticket.output", required=False, allow_none=True, many=True
    )


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
        output_param=restapi.Datamodel("helpdesk.ticket.output"),
    )
    def get(self, _id):
        record = self._get(_id)
        return self._return_record(record)

    @restapi.method(
        routes=[(["/"], "GET")],
        output_param=restapi.Datamodel("helpdesk.ticket.output"),
    )
    def search(self):
        domain = self._get_base_search_domain()
        records = self.env[self._expose_model].search(domain)
        result = {"size": len(records), "data": self._to_json(records, many=True)}
        return self.env.datamodels["helpdesk.ticket.search.output"].load(result)

    @restapi.method(
        routes=[(["/create"], "POST")],
        input_param=restapi.Datamodel("helpdesk.ticket.input"),
        output_param=restapi.Datamodel("helpdesk.ticket.output"),
    )
    # pylint: disable=W8106
    def create(self, ticket):
        vals = self._prepare_params(ticket.dump(), mode="create")
        record = self.env[self._expose_model].create(vals)
        return self._return_record(record)

    @restapi.method(
        routes=[(["/<int:id>"], "DELETE")],
        output_param=restapi.Datamodel("empty.output"),
    )
    def cancel(self, _id):
        stage_cancelled = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_cancelled")
        record = self._get(_id)
        record.stage_id = stage_cancelled
        return self.env.datamodels["empty.output"].load({})

    def _prepare_params(self, params, mode="create"):
        params = super()._prepare_params(params, mode=mode)
        if mode == "create":
            if self.env.context.get("authenticated_partner_id"):
                params["partner_id"] = self.env.context.get("authenticated_partner_id")
                params.pop("partner", None)
            elif params.get("partner"):
                partner = params.pop("partner")
                params["partner_name"] = partner.pop("name")
                if partner.get("email"):
                    try:
                        params["partner_id"] = (
                            self.env["res.partner"]
                            .find_or_create(partner["email"], assert_valid_email=True)
                            .id
                        )
                        params["partner_email"] = partner.pop("email")
                    except ValueError:
                        raise UserError(_("The email is not valid"))
                else:
                    raise UserError(_("The partner is mandatory"))
        for key in ["category", "team"]:
            if key in params:
                val = params.pop(key)
                if val.get("id"):
                    params["%s_id" % key] = val["id"]
        return params

    def _json_parser(self):
        res = [
            "id",
            "name",
            "description",
            "create_date",
            "last_stage_update",
            ("category_id:category", ["id", "name"]),
            ("team_id:team", ["id", "name"]),
            ("stage_id:stage", ["id", "name"]),
        ]
        res += self._json_parser_messages()
        res += self._json_parser_attachments()
        return res

    def _get_base_search_domain(self):
        res = super()._get_base_search_domain()
        res += [("partner_id", "=", self.env.context.get("authenticated_partner_id"))]
        return res
