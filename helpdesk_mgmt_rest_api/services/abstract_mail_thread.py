# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.base_rest import restapi
from odoo.addons.component.core import AbstractComponent
from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class MailPartnerOutput(Datamodel):
    _name = "mail.partner.output"

    id = fields.Integer(required=False, allow_none=False)
    name = fields.String(required=True, allow_none=False)


class MailMessageBase(Datamodel):
    _name = "mail.message.base"

    body = fields.String(required=True, allow_none=False)


class MailMessageInput(Datamodel):
    _name = "mail.message.input"
    _inherit = ["mail.message.base", "attachable.input"]


class MailMessageOutput(Datamodel):
    _name = "mail.message.output"
    _inherit = "mail.message.base"

    id = fields.Integer(required=False, allow_none=False)
    date = fields.DateTime(required=False, allow_none=False)
    author = fields.NestedModel("mail.partner.output", required=True, allow_none=False)


class MailThreadOutput(Datamodel):
    _name = "mail.thread.output"

    messages = fields.NestedModel("mail.message.output", required=True, many=True)


class AbstractMailThreadService(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "mail.thread.abstract.service"

    @restapi.method(
        routes=[(["/<int:id>/send_message"], "POST")],
        input_param=restapi.Datamodel("mail.message.input"),
        # output_param=restapi.Datamodel("{}.output".format(_expose_model)),
    )
    def send_message(self, _id, message):
        record = self._get(_id)
        vals = self._prepare_message_params(record, message.dump())
        record.write({"message_ids": [(0, 0, vals)]})
        return self._return_record(record).dump()

    def _get_base_search_domain(self):
        # TODO: make it work
        return [("is_internal", "=", False)]

    def _prepare_message_params(self, record, params):
        params["model"] = self._expose_model
        params["author_id"] = self.env.context["authenticated_partner_id"]
        if params.get("attachments"):
            attachments = params.pop("attachments")
            params["attachment_ids"] = [(6, 0, [item["id"] for item in attachments])]
        return params

    def _json_parser_messages(self):
        res = [("message_ids:messages", self._json_parser_message())]
        return res

    def _json_parser_message(self):
        return [
            "id",
            "body",
            "date",
            ("author_id:author", ["id", "name"]),
        ]
