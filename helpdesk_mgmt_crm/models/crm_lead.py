# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket", string="Helpdesk Ticket"
    )
