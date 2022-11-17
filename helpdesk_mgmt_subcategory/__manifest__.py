# © 2022 Rafa Morant <rmorant@albasoft.com>

{
    "name": "Helpdesk Subcategories",
    "summary": "",
    "version": "14.0.1.0.0",
    "category": "Customize",
    "license": "AGPL-3",
    "author": "ALBA Software, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt"],
    "data": [
        "data/model-data.xml",
        "views/helpdesk_ticket_category_ex.xml",
        "views/helpdesk_ticket_team.xml",
        "views/helpdesk_ticket.xml",
        "views/helpdesk_ticket_tag_viex.xml",
    ],
    "demo": ["demo/helpdesk_category_demo.xml"],
    "development_status": "Beta",
    "installable": True,
}
