# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicketCategory(models.Model):
    _inherit = "helpdesk.ticket.category"

    form_id = fields.Many2one(
        comodel_name="helpdesk.ticket.form",
        string="Portal Form",
        help="Structured question form shown in the portal when this category "
        "is selected. If empty, the standard free-text description is used.",
    )
