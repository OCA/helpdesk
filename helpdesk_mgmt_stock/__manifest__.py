# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Mgmt Stock",
    "summary": """This module allows to create helpdesk tickets during stock operations""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/helpdesk",
    "depends": [
        "helpdesk_mgmt",
        "helpdesk_product",
        "stock",
        "helpdesk_motive",
    ],
    "data": [
        "views/helpdesk_ticket_motive.xml",
        "security/security.xml",
        "views/stock_move.xml",
        "views/stock_picking.xml",
        "views/helpdesk_ticket.xml",
        "wizards/stock_helpdesk_ticket_create.xml",
        "views/stock_picking_type.xml",
    ],
    "demo": [],
}
