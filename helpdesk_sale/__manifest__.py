# Copyright (C) 2020 Callino
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Sale Order",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Create Sale Order from Ticket",
    "author": "Callino, Wolfgang Pichler, "
              "Odoo Community Association (OCA)",
    "website": "https://githut.com/OCA/helpdesk",
    "depends": [
        "helpdesk_mgmt", "sale",
    ],
    "data": [
        "views/helpdesk_ticket.xml",
        "views/sale_order.xml",
    ],
    "application": False,
    "development_status": "Stable",
    "maintainers": [
        "wpichler@callino.at",
    ],
}
