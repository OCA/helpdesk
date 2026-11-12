# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Ticket Equipment (Portal)",
    "summary": "Pick the equipment (and location) when opening a ticket "
    "from the portal",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/helpdesk",
    "category": "After-Sales",
    "author": "Pop Solutions, Odoo Community Association (OCA)",
    "maintainers": ["marcos-mendez"],
    "depends": ["helpdesk_mgmt_fieldservice_equipment"],
    "data": [
        "views/portal_templates.xml",
        "views/helpdesk_ticket_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "helpdesk_mgmt_fieldservice_equipment_portal/static/src/js/portal_ticket_equipment.js",
        ],
    },
}
