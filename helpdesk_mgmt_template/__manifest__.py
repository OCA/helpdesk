# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Management Template",
    "summary": "Create Helpdesk Ticket Template",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Cetmix OÜ, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt"],
    "data": [
        "views/helpdesk_ticket_views.xml",
        "views/helpdesk_ticket_category_views.xml",
        "views/helpdesk_ticket_team_views.xml",
    ],
    "application": False,
}
