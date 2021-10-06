# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.base_rest import restapi
from odoo.addons.component.core import AbstractComponent

from .abstract_attachment import AbstractAttachmentService


class AbstractMailThreadService(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "mail.thread.abstract.service"

    @restapi.method(
        routes=[(["/create"], "POST")],
        input_param=restapi.CerberusValidator("_validator_send_message"),
    )
    def send_message(self, _id, **params):
        record = self._get(_id)
        vals = self._prepare_message_params(record, params)
        record.write({"message_ids": [(0, 0, vals)]})
        return self._to_json(record)

    def _validator_send_message(self):
        res = AbstractAttachmentService._validator_attachment(self)
        res.update(
            {
                "body": {"type": "string", "required": True},
            }
        )
        return res

    def _prepare_message_params(self, record, params):
        params["model"] = self._expose_model
        params["author_id"] = self.env.context["authenticated_partner_id"]
        if params.get("attachments"):
            attachments = params.pop("attachments")
            params["attachment_ids"] = [(6, 0, [item["id"] for item in attachments])]
        return params

    def _json_parser(self):
        res = [("message_ids:messages", self._json_parser_message())]
        return res

    def _json_parser_message(self):
        return [
            "id",
            "body",
            "date",
            ("author_id:author", ["id", "name"]),
        ]
