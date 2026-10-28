# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Helpdesk Partner Dashboard",
    "summary": """
        Replace the Helpdesk team dashboard with one grouped by customer""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "category": "After-Sales",
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt"],
    "data": [
        "views/helpdesk_ticket_views.xml",
        "views/res_partner_views.xml",
        "views/helpdesk_ticket_menu.xml",
    ],
    "installable": True,
    "uninstall_hook": "uninstall_hook",
}
