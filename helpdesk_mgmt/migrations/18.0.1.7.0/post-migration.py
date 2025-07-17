from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    menu = env.ref("helpdesk_mgmt.helpdesk_ticket_menu", raise_if_not_found=False)
    if menu:
        menu.write({"action": False})
