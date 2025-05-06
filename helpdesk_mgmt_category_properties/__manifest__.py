{
    "name": "Helpdesk Category Properties",
    "summary": "Add custom properties to helpdesk tickets based on their category",
    "version": "16.0.1.0.0",
    "category": "Helpdesk",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "depends": ["helpdesk_mgmt"],
    "data": [
        "views/helpdesk_ticket_category_views.xml",
        "views/helpdesk_ticket_views.xml",
    ],
    "installable": True,
}
