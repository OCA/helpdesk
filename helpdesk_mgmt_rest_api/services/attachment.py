# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from babel.dates import format_datetime
from werkzeug.exceptions import NotFound

from odoo import _
from odoo.exceptions import UserError
from odoo.http import request

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class AttachmentService(Component):
    _name = "attachment.service"
    _inherit = "base.helpdesk.rest.service"
    _usage = "attachment"
    _expose_model = "ir.attachment"

    def get(self, _id):
        record = self._get(_id)
        return self._to_json(record)

    def update(self, _id, **params):
        record = self._get(_id)
        vals = self._prepare_params(None, params)
        record.write(vals)
        return self._to_json(record)

    @restapi.method(
        routes=[(["/create"], "POST")],
        input_param=restapi.CerberusValidator("_validator_create"),
    )
    # pylint: disable=W8106
    def create(self):
        req = request.httprequest
        vals = self._prepare_params(req, {})
        record = self.env[self._expose_model].create(vals)
        return self._to_json(record)

    def _validator_create(self):
        validator_json = self._validator_update()
        validator_json["raw"] = {"type": "string", "format": "binary"}
        return validator_json

    def _validator_update(self):
        return {
            "name": {
                "type": "string",
                "nullable": True,
            },
            "res_id": {"type": "integer", "coerce": to_int, "nullable": True},
            "res_model": {"type": "string", "nullable": True},
        }

    def _prepare_params(self, req, params):
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

        if req:
            file_ext = req.content_type.split("/")[1]
            params["name"] = "client_upload.{}".format(file_ext)
            partner = self.env["res.partner"].browse(
                self.env.context.get("authenticated_partner_id")
            )
            partner_email = "anonymous"
            if partner:
                partner_email = partner.email
            params["description"] = (
                "Created by {} on {}".format(
                    partner_email,
                    format_datetime(datetime.datetime.now()),
                ),
            )
            params["raw"] = req.get_data()
        return params

    def _validator_get(self):
        return {}

    def _json_parser(self):
        res = ["id", "name", "res_id", "res_model", "res_name"]
        return res

    def _to_json(self, attachment, **kw):
        data = attachment.jsonify(self._json_parser())
        return data
