# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController


class HelpdeskTicketControllerInherit(HelpdeskTicketController):
    def _prepare_submit_ticket_vals(self, **kw):
        vals = super()._prepare_submit_ticket_vals(**kw)
        # original code uses the “plaintext2html” function,
        # so the image is converted into text instead of being rendered
        # as an actual image in the tickets.
        # To prevent that, we removed the function
        vals["description"] = kw.get("description")

        return vals
