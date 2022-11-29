# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Management - Nonconformity",
    "summary": "Links helpdesk tickets with nonconformities",
    "version": "15.0.1.0.0",
    "category": "After-Sales",
    "website": "https://github.com/OCA/helpdesk",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["helpdesk_mgmt", "mgmtsystem_nonconformity"],
    "data": [
        "data/helpdesk_ticket_stage.xml",
        "views/helpdesk_ticket_view.xml",
        "views/helpdesk_ticket_stage_view.xml",
        "views/mgmtsystem_nonconformity_view.xml",
    ],
    "installable": True,
    "maintainers": ["victoralmau"],
}
