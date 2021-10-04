# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import AbstractComponent


class AbstractAttachmentService(AbstractComponent):
    """Shopinvader abstract service to allow to use attachments on a service."""

    _name = "abstract.attachment.service"
    _inherit = "base.rest.service"
    _description = __doc__

    # pylint: disable=W8106
    def create(self, **params):
        attachments = params.pop("attachments", [])
        vals = self._prepare_params(params.copy(), mode="create")
        record = self.env[self._expose_model].create(vals)
        self._post_create_link_attachment(record, [item["id"] for item in attachments])
        return {"data": self._to_json(record)}

    def _post_create_link_attachment(self, record, attachment_ids):
        if len(attachment_ids) > 0:
            attachments = self.env["ir.attachment"].browse(attachment_ids)
            attachments.write({"res_model": record._name, "res_id": record.id})

    def _validator_create(self):
        return self._validator_attachment()

    def _validator_attachment(self):
        return {
            "attachments": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "id": {
                            "type": "integer",
                            "coerce": to_int,
                            "nullable": True,
                        },
                    },
                },
            },
        }

    def _json_parser(self):
        return [
            ("attachment_ids:attachments", ["id", "name"]),
        ]

    def _prepare_params(self, params, mode="create"):
        return NotImplementedError

    def _to_json(self, record):
        return NotImplementedError
