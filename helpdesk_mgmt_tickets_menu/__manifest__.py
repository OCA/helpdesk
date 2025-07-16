# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Helpdesk Ticket Menu",
    "summary": """
    Split the ticket menu to display the 'My Tickets' and 'All Tickets' submenus
    """,
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "category": "After-Sales",
    "version": "17.0.1.0.0",
    "depends": [
        "helpdesk_mgmt",
    ],
    "data": [
        "views/helpdesk_mgmt_tickets_menu.xml",
    ],
    "uninstall_hook": "uninstall_hook",
}
