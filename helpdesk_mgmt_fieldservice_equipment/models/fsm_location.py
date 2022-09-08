# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    equipment_ids = fields.One2many("fsm.equipment", "location_id", string="Equipments")

