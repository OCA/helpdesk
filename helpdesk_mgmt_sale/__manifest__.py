{
    "name": "Helpdesk Sale",
    "summary": "Manage sales info on an helpdesk ticket",
    "version": "14.0.1.0.0",
    "category": "Helpdesk",
    "website": "https://github.com/OCA/helpdesk",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "helpdesk_mgmt",
        "sale",
    ],
    "data": [
        "views/ticket_view.xml",
        "security/ir.model.access.csv",
    ],
}
