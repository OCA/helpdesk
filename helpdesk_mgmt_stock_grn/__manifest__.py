# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Mgmt Stock Grn",
    "summary": """Enables to link a GRN to helpdesk ticket""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt_stock", "stock_grn"],
    "data": [
        "views/helpdesk_ticket.xml",
    ],
    "demo": [],
}
