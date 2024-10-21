# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Management Activity",
    "summary": "Create Activities for Odoo records from the Helpdesk",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Cetmix OÜ, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/helpdesk_ticket_view.xml",
        "views/mail_activity_views.xml",
        "views/helpdesk_ticket_team_views.xml",
    ],
    "application": False,
}
