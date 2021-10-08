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

    def _create(self, params):
        attachments = params.pop("attachments", [])
        vals = self._prepare_params(params.copy(), mode="create")
        record = self.env[self._expose_model].create(vals)
        self._post_create_link_attachment(record, [item["id"] for item in attachments])
        return record

    def _post_create_link_attachment(self, record, attachment_ids):
        if len(attachment_ids) > 0:
            attachments = self.env["ir.attachment"].browse(attachment_ids)
            attachments.write({"res_model": record._name, "res_id": record.id})

    def _json_parser_attachments(self):
        res = [
            ("attachment_ids:attachments", ["id", "name"]),
        ]
        return res
