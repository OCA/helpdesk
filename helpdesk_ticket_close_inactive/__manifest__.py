# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Ticket Close Inactive",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Helpdesk",
    "website": "https://github.com/OCA/helpdesk",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["miquelalzanillas"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "helpdesk_mgmt",
    ],
    "data": [
        "views/helpdesk_ticket_team.xml",
        "data/helpdesk_data.xml",
    ],
}
