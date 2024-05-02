# Copyright (C) 2024 Irlui Ramírez <iramirez.spain@gmail.com>
# Copyright (C) 2024 Consultores Hoteleros Integrales <www.aldahotels.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HelpdeskTeam(models.Model):

    _inherit = "helpdesk.ticket"

    default_zone = fields.Selection(
        string="Default Name Zone",
        selection=[
            ("cs_coffe_shop", "CS-Coffe Shop"),
            ("zr_zone_rooms", "ZR-Zone Rooms"),
            ("p_parking", "PA-Parking"),
            ("el-elevator", "EL-Elevator"),
            ("ac_climatic", "AC-Climatic"),
            ("re-reception", "RE-Reception"),
        ],
        default="re-reception",
    )
