# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright (C) 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import html2plaintext


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    fsm_order_ids = fields.One2many("fsm.order", "ticket_id", string="Service Orders")
    fsm_location_id = fields.Many2one(
        "fsm.location",
        string="FSM Location",
        compute="_compute_fsm_location_id",
        store=True,
        readonly=False,
    )
    resolution = fields.Text()

    @api.constrains("stage_id")
    def _validate_stage_fields(self):
        for rec in self:
            if (
                self.stage_id.closed
                and rec.fsm_order_ids
                and not all(rec.fsm_order_ids.mapped("stage_id.is_closed"))
            ):
                raise ValidationError(
                    self.env._(
                        "Please complete all service orders "
                        "related to this ticket to close it."
                    )
                )

    @api.depends("partner_id")
    def _compute_fsm_location_id(self):
        # When changing the partner, the default service location is set
        # Unless the existing location is valid for the new partner
        for rec in self:
            if not rec.partner_id:
                continue
            if (
                rec.partner_id.commercial_partner_id
                == rec.fsm_location_id.commercial_partner_id
            ):
                continue
            if rec.partner_id.service_location_id:
                rec.fsm_location_id = rec.partner_id.service_location_id
            elif rec.partner_id.commercial_partner_id.service_location_id:
                rec.fsm_location_id = (
                    rec.partner_id.commercial_partner_id.service_location_id
                )

    def action_create_order(self):
        """
        This function returns an action that displays a full FSM Order
        form when creating an FSM Order from a ticket.
        """
        action = self.env["ir.actions.actions"]._for_xml_id(
            "fieldservice.action_fsm_operation_order"
        )
        # override the context to get rid of the default filtering
        action["context"] = {
            "default_ticket_id": self.id,
            "default_priority": self.priority,
            "default_location_id": self.fsm_location_id.id,
            "default_description": html2plaintext(self.description).strip(),
        }
        res = self.env.ref("fieldservice.fsm_order_form", False)
        action["views"] = [(res and res.id or False, "form")]
        return action
