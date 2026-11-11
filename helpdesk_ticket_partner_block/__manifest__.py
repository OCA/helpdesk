# Copyright 2026 Paloma González-Ripoll(APSL-Nagarro)<paloma.gonzalez@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Ticket Partner Block",
    "summary": "Block helpdesk ticket creation by email for specific contacts",
    "version": "18.0.1.0.0",
    "category": "Helpdesk",
    "website": "https://github.com/OCA/helpdesk",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["palomagrc93"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["helpdesk_mgmt"],
    "data": [
        "data/mail_template_data.xml",
        "views/res_partner_views.xml",
    ],
}
