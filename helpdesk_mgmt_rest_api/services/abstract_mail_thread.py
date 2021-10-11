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
        routes=[(["/<int:id>/message_post"], "POST")],
        input_param=restapi.Datamodel("mail.message.input"),
        output_param=restapi.Datamodel("mail.message.output"),
    )
    def message_post(self, _id, message):
        record = self._get(_id)
        kwargs = self._prepare_message_post_params(message.dump())
        message = record.message_post(**kwargs)
        # record.write({"message_ids": [(0, 0, vals)]})
        # return self._return_record(record).dump()
        return self.env.datamodels["mail.message.output"].load(
            message.jsonify(self._json_parser_message())[0]
        )

    def _prepare_message_post_params(self, params):
        params["author_id"] = self.env.context["authenticated_partner_id"]
        params["message_type"] = "comment"
        params["subtype_id"] = self.env["ir.model.data"].xmlid_to_res_id(
            "mail.mt_comment"
        )
        if params.get("attachments"):
            attachments = params.pop("attachments")
            params["attachment_ids"] = [item["id"] for item in attachments]
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
