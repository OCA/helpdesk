# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Sale Order",
    "summary": "Add the option to select project in the sale orders.",
    "version": "18.0.2.0.0",
    "license": "AGPL-3",
    "category": "Sales Management",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_views.xml",
        "views/sale_order_views.xml",
        "wizards/helpdesk_ticket_link_sale_order.xml",
    ],
    "development_status": "Production/Stable",
    "auto_install": True,
}
