# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Helpdesk Ticket Team Partner",
    "category": "Helpdesk",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "summary": (
        "Allows dynamic control over which contact (partner_id) on ticket, "
        "based on the configuration of the assigned Helpdesk Team (team_id)"
    ),
    "author": "Solvosci, " "Odoo Community Association (OCA)",
    "depends": ["helpdesk_mgmt"],
    "version": "17.0.1.0.0",
    "data": [
        "views/helpdesk_ticket_views.xml",
        "views/helpdesk_ticket_team_views.xml",
    ],
    "application": False,
    "installable": True,
}
