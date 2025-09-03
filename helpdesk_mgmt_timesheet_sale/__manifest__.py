# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Mgmt Timesheet Sale",
    "summary": """Allow to set the sale order line directly on helpdesk tickets""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": [
        "helpdesk_mgmt_timesheet",
        "sale_timesheet",
    ],
    "data": [
        "views/helpdesk_ticket.xml",
    ],
    "demo": [],
}
