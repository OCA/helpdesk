# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import AbstractComponent
from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class AttachInput(Datamodel):
    _name = "attach.input"

    id = fields.Integer(required=True)


class AttachableInput(Datamodel):
    _name = "attachable.input"

    attachments = fields.NestedModel("attach.input", required=False, many=True)


class AttachableOutput(Datamodel):
    _name = "attachable.output"

    attachments = fields.NestedModel("ir.attachment.output", required=False, many=True)


class AbstractAttachableService(AbstractComponent):
    """Abstract service to allow to use attachments on a service."""

    _name = "abstract.attachable.service"
    _inherit = "base.rest.service"
    _description = __doc__

    def _prepare_params(self, params, mode="create"):
        if "attachments" in params:
            attachments = params.pop("attachments", None)
            if attachments:
                params["attachment_ids"] = [
                    (6, 0, [item["id"] for item in attachments])
                ]
        return params

    def _json_parser_attachments(self):
        res = [
            ("attachment_ids:attachments", ["id", "name"]),
        ]
        return res
