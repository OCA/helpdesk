# Copyright (C) 2024 Irlui Ramírez <iramirez.spain@gmail.com>
# Copyright (C) 2024 Consultores Hoteleros Integrales <www.aldahotels.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HelpdeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    property_id = fields.Many2one(
        comodel_name="pms.property",
        string="Property",
        domain="[('company_id', '=', company_id)]",
        help="The property associated with this ticket",
    )
    room_id = fields.Many2one(
        comodel_name="pms.room",
        string="Room",
        domain="[('pms_property_id', '=', property_id)]",
        help="The room associated with this ticket",
        widget="many2one_tags",
    )

    @api.depends("company_id")
    def _onchange_company_id(self):
        if self.company_id:
            properties = (
                self.env["pms.property"]
                .sudo()
                .search([("user_ids", "=", self.env.user.id)])
            )
            property_ids = properties.ids if properties else []
            return {"domain": {"property_id": [("id", "in", property_ids)]}}
        else:
            return {"domain": {"property_id": []}}

    @api.depends("property_id")
    def _onchange_property_id(self):
        if self.property_id:
            rooms = (
                self.env["pms.room"]
                .sudo()
                .search([("pms_property_id", "=", self.property_id.id)])
            )
            room_ids = rooms.ids if rooms else []
            return {"domain": {"room_id": [("id", "in", room_ids)]}}
        else:
            return {"domain": {"room_id": []}}
