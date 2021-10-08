# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from werkzeug.exceptions import NotFound

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class AttachmentBase(Datamodel):
    _name = "ir.attachment.base"

    name = fields.String(required=True, allow_none=False)
    res_id = fields.Integer(required=False, allow_none=False)
    res_model = fields.String(required=False, allow_none=False)


class AttachmentInput(Datamodel):
    _name = "ir.attachment.input"
    _inherit = "ir.attachment.base"


class AttachmentOutput(Datamodel):
    _name = "ir.attachment.output"
    _inherit = "ir.attachment.base"

    id = fields.Integer(required=True, allow_none=False)
    res_name = fields.String(required=False, allow_none=False)


class AttachmentService(Component):
    _name = "attachment.service"
    _inherit = "base.helpdesk.rest.service"
    _usage = "attachment"
    _expose_model = "ir.attachment"

    #    @restapi.method(
    #            routes=[(["/<int:id>"], "GET")],
    #            output_param=restapi.Datamodel("ir.attachment.output"),
    #    )
    #    def get(self, _id):
    #        raise AccessError()
    #
    #    @restapi.method(
    #        routes=[(["/update"], "POST")],
    #        input_param=restapi.Datamodel("ir.attachment.input"),
    #    )
    #    def update(self, _id, attachment):
    #        raise AccessError

    @restapi.method(
        routes=[(["/create"], "POST")],
        input_param=restapi.MultipartFormData(
            [
                restapi.BinaryFormDataPart("file"),
                restapi.JsonFormDataPart(
                    "params", restapi.Datamodel("ir.attachment.input")
                ),
            ]
        ),
        output_param=restapi.Datamodel("ir.attachment.output"),
    )
    # pylint: disable=W8106
    def create(self, **params):
        vals = self._prepare_params(params)
        record = self.env[self._expose_model].create(vals)
        return self._to_json(record)

    def _prepare_params(self, params):
        # Extract params from multipart form part
        if "params" in params:
            params.update(json.loads(params.pop("params")))
        if params.get("res_id") and params.get("res_model"):
            record = self.env[params["res_model"]].browse(params["res_id"])
            if len(record) != 1:
                raise NotFound(
                    "The targeted record does not exist: {}({})".format(
                        params["res_model"], params["res_id"]
                    )
                )
        elif not params.get("res_id") and not params.get("res_model"):
            pass
        else:
            raise UserError(_("You must provide both res_model and res_id"))
        if "file" in params:
            uploaded_file = params.pop("file")
            params["raw"] = uploaded_file.read()
            if "name" not in params:
                params["name"] = uploaded_file.filename
        return params

    def _json_parser(self):
        res = ["id", "name", "res_id", "res_model", "res_name"]
        return res
