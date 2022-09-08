# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

class FSMOrder(models.Model):
    _inherit = "fsm.order"

    type = fields.Many2one("fsm.order.type", string="Type", default=1)