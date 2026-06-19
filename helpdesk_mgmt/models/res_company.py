# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    helpdesk_mgmt_portal_select_team = fields.Boolean(
        string="Select team in Helpdesk portal"
    )
    helpdesk_mgmt_portal_team_id_required = fields.Boolean(
        string="Required Team field in Helpdesk portal",
        default=True,
    )
    helpdesk_mgmt_portal_select_category = fields.Boolean(
        string="Select category in Helpdesk portal"
    )
    helpdesk_mgmt_portal_category_id_required = fields.Boolean(
        string="Required Category field in Helpdesk portal",
        default=True,
    )
    helpdesk_mgmt_duplicate_tracking = fields.Boolean(
        string="Enable duplicate ticket tracking.", default=False
    )
    helpdesk_mgmt_duplicate_ticket_stage_id = fields.Many2one(
        comodel_name="helpdesk.ticket.stage",
        string="Move duplicate tickets to this stage",
        default=False,
    )
    helpdesk_mgmt_ticket_auto_assign = fields.Boolean(
        string="Auto assign tickets",
        default=True,
    )
    helpdesk_mgmt_autoreply_ignored_partners = fields.Many2many(
        comodel_name="res.partner",
        relation="helpdesk_mgmt_company_autoreply_ignored_partner_rel",
        column1="company_id",
        column2="partner_id",
        string="Auto-reply ignored partners",
        domain=[("email", "!=", False)],
        help="Partners whose email address will not receive an automatic reply "
        "when a helpdesk ticket is created from their email.",
    )
