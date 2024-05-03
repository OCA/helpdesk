# Copyright (C) 2024 Irlui Ramírez <iramirez.spain@gmail.com>
# Copyright (C) 2024 Consultores Hoteleros Integrales <www.aldahotels.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HelpdeskCategory(models.Model):

    _inherit = "helpdesk.ticket.category"

    pms_property_ids = fields.Many2many(
        string="Properties",
        help="Properties with access to the element"
        " if not set, all properties can access",
        comodel_name="pms.property",
        relation="helpdesk_ticket_category_pms_property_rel",
        column1="helpdesk_ticket_category_id",
        column2="pms_property_id",
        required=False,
        ondelete="restrict",
        check_pms_properties=True,
    )
