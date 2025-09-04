# Copyright 2025 Marcel Savegnago - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    helpdesk_mgmt_project_domain = fields.Char(
        string="Project Domain",
        help="Global domain to filter projects available for selection in tickets. "
        "This will be applied if no specific domain is set in the team. "
        "Example: [('active', '=', True), ('partner_id', '!=', False)]",
    )

    helpdesk_mgmt_task_domain = fields.Char(
        string="Task Domain",
        help="Global domain to filter tasks available for selection in tickets. "
        "This will be applied if no specific domain is set in the team. "
        "Example: [('active', '=', True), ('project_id', '!=', False)]",
    )
