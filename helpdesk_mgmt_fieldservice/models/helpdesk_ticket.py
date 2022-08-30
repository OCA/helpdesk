# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright (C) 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    fsm_order_ids = fields.One2many("fsm.order", "ticket_id", string="Service Orders")
    fsm_location_id = fields.Many2one("fsm.location", string="FSM Location")
    all_orders_closed = fields.Boolean(compute="_compute_all_closed", store=True)
    resolution = fields.Text(string="Resolution")
    # these fields are needed to obtain depreciation of onchange in v14
    partner_domain = fields.Integer(compute="_compute_partner_domain")
    all_partners = fields.Boolean(compute="_compute_partner_domain")

    @api.constrains("stage_id")
    def _validate_stage_fields(self):
        for rec in self:
            stage = rec.stage_id
            if stage.closed:
                if rec.fsm_order_ids:
                    closed_orders = rec.fsm_order_ids.filtered(
                        lambda x: x.stage_id.is_closed
                    )
                    if len(closed_orders.ids) != len(rec.fsm_order_ids):

                        raise ValidationError(
                            _(
                                "Please complete all service orders "
                                "related to this ticket to close it."
                            )
                        )

    def _location_contact_fill(self, loc):
        """loc is a boolean that lets us know if this is coming from the
        partner onchange or the location onchange"""
        if loc:
            if self.fsm_location_id and self.partner_id:
                if self.partner_id.service_location_id != self.fsm_location_id:
                    self.partner_id = False
        else:
            if self.partner_id:
                if not self.fsm_location_id:
                    self.fsm_location_id = self.partner_id.service_location_id

    # Updating domain via onchange is deprecated in odoo v14
    @api.depends("fsm_location_id")
    def _compute_partner_domain(self):
        for rec in self:
            rec.partner_domain = False
            rec.all_partners = True
            if rec.fsm_location_id:
                rec._location_contact_fill(True)
                if rec.fsm_location_id and not rec.partner_id:
                    rec.partner_domain = rec.fsm_location_id.id
                    rec.all_partners = False

    @api.onchange("partner_id")
    def _onchange_partner_id_location(self):
        if self.partner_id:
            self._location_contact_fill(False)

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
        }
        res = self.env.ref("fieldservice.fsm_order_form", False)
        action["views"] = [(res and res.id or False, "form")]
        return action

    @api.depends("fsm_order_ids", "stage_id", "fsm_order_ids.stage_id")
    def _compute_all_closed(self):
        for ticket in self:
            ticket.all_orders_closed = True
            if ticket.fsm_order_ids:
                for order in ticket.fsm_order_ids:
                    if order.stage_id.name not in ["Closed", "Cancelled"]:
                        ticket.all_orders_closed = False
            else:
                ticket.all_orders_closed = False
