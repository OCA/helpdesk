# Copyright (C) 2026 Popsolutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController


class HelpdeskTicketControllerEquipment(HelpdeskTicketController):
    """Let portal customers pick the equipment (and its location) when
    opening a ticket from /new/ticket.

    - Only equipments owned by the commercial partner of the logged-in user
      are accepted.
    - The ticket location is derived from the equipment on the server side,
      which satisfies the `_check_equipment_location` constraint of
      helpdesk_mgmt_fieldservice_equipment.
    """

    def _get_portal_commercial_partner(self):
        return request.env.user.partner_id.commercial_partner_id

    def _get_portal_equipments(self):
        partner = self._get_portal_commercial_partner()
        # fsm.equipment has no `active` field
        return (
            request.env["fsm.equipment"]
            .sudo()
            .search([("owned_by_id", "=", partner.id)], order="name")
        )

    def _get_create_new_ticket_values(self, **kw):
        values = super()._get_create_new_ticket_values(**kw)
        equipments = self._get_portal_equipments()
        values["equipments"] = equipments
        values["equipment_locations"] = equipments.location_id.sorted(
            lambda loc: loc.display_name or ""
        )
        return values

    def _prepare_submit_ticket_vals(self, **kw):
        vals = super()._prepare_submit_ticket_vals(**kw)
        try:
            equipment_id = int(kw.get("equipment") or 0)
        except (TypeError, ValueError):
            equipment_id = 0
        if equipment_id:
            # filtered() instead of browse(): enforce ownership by the portal partner
            equipment = self._get_portal_equipments().filtered(
                lambda eq: eq.id == equipment_id
            )
            if equipment:
                vals["equipment_id"] = equipment.id
                if equipment.location_id:
                    vals["fsm_location_id"] = equipment.location_id.id
        return vals
