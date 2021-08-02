{
    "name": "Helpdesk Management Rating",
    "summary": """
        This module allows customer to rate the assistance received
        on a ticket.
        """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Domatix, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "category": "After-Sales",
    "depends": ["helpdesk_mgmt", "rating"],
    "data": [
        "data/helpdesk_data.xml",
        "views/helpdesk_ticket_menu.xml",
        "views/helpdesk_ticket_views.xml",
        "views/helpdesk_ticket_stage_views.xml",
    ],
    "installable": True,
}
