# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Helpdesk Ticket Portal Cat Assignment",
    "category": "Helpdesk",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "summary": (
        "Auto-assign portal tickets to a default internal "
        "user configured in Helpdesk."
    ),
    "author": "Solvosci, " "Odoo Community Association (OCA)",
    "depends": ["helpdesk_mgmt"],
    "version": "17.0.1.0.0",
    "data": ["views/helpdesk_ticket_category_views.xml"],
    "application": False,
    "installable": True,
}
