# Copyright 2020 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def _prepare_ticket_number(self, values):
        seq = False
        if values.get("partner_id") or self.partner_id:
            partner = (
                self.env["res.partner"].browse(values["partner_id"])
                if "partner_id" in values
                else self.partner_id
            )
            company_id = values.get("company_id", self.company_id.id)
            # look for ticket sequence in partner
            seq = partner.helpdesk_ticket_sequence_id
            if seq.company_id and seq.company_id.id != company_id:
                seq = False
            if partner.parent_id and not seq:
                # look for ticket sequence in partner parent
                seq = partner.parent_id.helpdesk_ticket_sequence_id
                if seq.company_id and seq.company_id.id != company_id:
                    seq = False
        if seq:
            return seq.next_by_id()
        else:
            return super()._prepare_ticket_number(values)
