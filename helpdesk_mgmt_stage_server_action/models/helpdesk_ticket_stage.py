# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicketStage(models.Model):
    _inherit = "helpdesk.ticket.stage"

    action_id = fields.Many2one(
        "ir.actions.server",
        string="Server Action",
        domain="[('model_id', '=', 'helpdesk.ticket')]",
        help="The assigned action will be executed when a ticket is assigned from a "
        "different stage to this stage, the context values that will be passed "
        "to the action are the model name helpdesk.ticket and the ids of the tickets.",
    )
