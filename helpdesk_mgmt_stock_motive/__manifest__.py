# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Mgmt Stock Motive",
    "summary": "Glue module to bridge helpdesk_mgmt_stock and helpdesk_motive",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/helpdesk",
    "depends": [
        "helpdesk_mgmt_stock",
        "helpdesk_motive",
    ],
    "data": [
        "views/helpdesk_ticket_motive_views.xml",
        "wizards/stock_helpdesk_ticket_create_views.xml",
    ],
    "demo": [],
}
