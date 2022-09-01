# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel
from odoo.addons.component.core import AbstractComponent

from ..pydantic_models.mail_message import MailMessageInfo, MailMessageRequest


class AbstractMailThreadService(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "mail.thread.abstract.service"

    @restapi.method(
        routes=[(["/<int:id>/message_post"], "POST")],
        input_param=PydanticModel(MailMessageRequest),
        output_param=PydanticModel(MailMessageInfo),
    )
    def message_post(self, _id, message):
        record = self._get(_id)
        kwargs = self._prepare_message_post_params(message.dict())
        message = record.message_post(**kwargs)
        return MailMessageInfo.from_orm(message)

    def _prepare_message_post_params(self, params):
        params["author_id"] = self.env.context["authenticated_partner_id"]
        params["message_type"] = "comment"
        params["subtype_id"] = self.env["ir.model.data"].xmlid_to_res_id(
            "mail.mt_comment"
        )
        attachments = params.pop("attachments", False)
        if attachments:
            params["attachment_ids"] = [item["id"] for item in attachments]
        return params
