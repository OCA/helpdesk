# Copyright 2024 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Ticket Merge",
    "summary": "Wizard to merge helpdesk tickets",
    "version": "18.0.1.0.0",
    "author": "Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "category": "After-Sales",
    "depends": ["helpdesk_mgmt"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/helpdesk_ticket_merge_views.xml",
    ],
    "installable": True,
}
