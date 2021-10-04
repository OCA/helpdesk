# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _
from odoo.exceptions import AccessError, UserError

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class TicketService(Component):
    """Shopinvader service to manage helpdesk tickets."""

    _name = "helpdesk.ticket.service"
    _inherit = [
        "mail.thread.abstract.service",
        "abstract.attachment.service",
    ]
    _usage = "helpdesk_ticket"
    _expose_model = "helpdesk.ticket"
    _description = __doc__

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    def get(self, _id):
        record = self._get(_id)
        return self._to_json(record)

    def search(self, **params):
        return self._paginate_search(**params)

    # pylint: disable=W8106
    def create(self, **params):
        return super().create(**params)

    def update(self, _id, **params):
        record = self._get(_id)
        record.write(self._prepare_params(params.copy(), mode="update"))
        return self.search()

    def cancel(self, _id):
        self._get(_id).unlink()  # TODO: cancel instead of delete
        return self.search()

    def _validator_get(self):
        return {}

    def _validator_search(self):
        return {
            "id": {"coerce": to_int, "type": "integer"},
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
            },
            "page": {"coerce": to_int, "nullable": True, "type": "integer"},
            "scope": {"type": "dict", "nullable": True},
        }

    def _validator_create(self):
        res = super()._validator_create()
        res.update(
            {
                "name": {"type": "string", "required": True, "empty": False},
                "description": {"type": "string", "required": True, "empty": False},
                "partner": {
                    "type": "dict",
                    "schema": {
                        "email": {
                            "type": "string",
                            "nullable": True,
                        },
                        "name": {
                            "type": "string",
                            "nullable": True,
                        },
                    },
                },
                "category": {
                    "type": "dict",
                    "schema": {
                        "id": {
                            "coerce": to_int,
                            "nullable": True,
                            "type": "integer",
                        },
                    },
                },
            }
        )
        return res

    def _prepare_params(self, params, mode="create"):
        if mode == "create":
            if self.partner_user:
                params["partner_id"] = self.partner_user.id
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
        for key in ["category"]:
            if key in params:
                val = params.pop(key)
                if val.get("id"):
                    params["%s_id" % key] = val["id"]
        return params

    def _json_parser(self):
        res = super()._json_parser()
        res.extend(
            [
                "id",
                "name",
                "description",
                "create_date",
                "last_stage_update",
                ("category_id:category", ["id", "name"]),
                ("stage_id:stage", ["id", "name"]),
            ]
        )
        return res

    def _to_json(self, ticket, **kw):
        data = ticket.jsonify(self._json_parser())
        return data

    def _get_base_search_domain(self):
        if not self.partner_user:
            raise AccessError(
                _("You should be connected to search for Helpdesk Tickets")
            )
        return [("partner_id", "=", self.partner_user.id)]
