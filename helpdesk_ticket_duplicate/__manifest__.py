# Copyright 2024 Tecnativa - David Bañón Gil
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Ticket Duplicate",
    "summary": "Allows marking a ticket as duplicate",
    "version": "18.0.1.0.0",
    "category": "Helpdesk",
    "website": "https://github.com/OCA/helpdesk",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["david-banon-tecnativa"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "helpdesk_mgmt",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/helpdesk_ticket_duplicate_wizard_views.xml",
        "views/helpdesk_ticket_views.xml",
        "data/helpdesk_ticket_duplicate_data.xml",
    ],
}
