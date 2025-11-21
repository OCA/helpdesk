# Copyright 2025 Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Mgmt Ticket Document Page",
    "summary": """Enable to associate a document_page on ticket""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "website": "https://github.com/OCA/helpdesk",
    "depends": [
        "helpdesk_mgmt",
        "document_page",
    ],
    "data": [
        "views/helpdesk_ticket.xml",
    ],
    "demo": [],
}
