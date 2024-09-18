# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Link between Helpdesk and CRM",
    "summary": "Links helpdesk tickets with leads",
    "version": "15.0.1.0.1",
    "category": "After-Sales",
    "website": "https://github.com/OCA/helpdesk",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["helpdesk_mgmt", "crm"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/helpdesk_ticket_create_lead_views.xml",
        "views/crm_lead_view.xml",
        "views/helpdesk_ticket_view.xml",
    ],
    "installable": True,
    "maintainers": ["victoralmau"],
}
