# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, registry, vals=None):
    env = api.Environment(cr, SUPERUSER_ID, {})

    env.ref("helpdesk_mgmt.helpdesk_ticket_menu").parent_id = env.ref(
        "helpdesk_mgmt.helpdesk_ticket_main_menu"
    ).id
