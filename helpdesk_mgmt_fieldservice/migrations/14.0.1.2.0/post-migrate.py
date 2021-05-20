from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Recalculate all_orders_closed after fix"""
    env = api.Environment(cr, SUPERUSER_ID, {"active_test": False})
    env["helpdesk.ticket"].search([])._compute_all_closed()
