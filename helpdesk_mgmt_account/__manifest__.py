# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Mgmt Account",
    "summary": """Link account moves and helpdesk tickets""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt", "account"],
    "data": [
        "views/helpdesk_ticket.xml",
        "views/account_move.xml",
    ],
    "demo": [],
}
