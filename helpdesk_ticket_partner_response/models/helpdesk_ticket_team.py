# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    autoupdate_ticket_stage = fields.Boolean(
        string="Auto Update Ticket Stage",
        help="Update ticket stage when a new message is registered by the partner.",
        default=False,
    )
    autopupdate_src_stage_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.stage",
        relation="change_stage_partner_response",
        string="Autoupdate Source Stages",
        help=(
            "If a partner posts a message in a ticket on this stages, "
            "the own stage of the ticket will be update by the one set on "
            "Autoupdate Destination Stage "
        ),
    )
    autopupdate_dest_stage_id = fields.Many2one(
        "helpdesk.ticket.stage",
        string="Autoupdate Destination Stage",
        help=("Target stage on partner's message post "),
    )
