# Copyright 2026 Solvos Consultoria Informatica
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Ticket Message Contact Default Unchecked",
    "summary": """
        By default, when you create a ticket with a selected
        contact or send a message, the “Add as follower and recipient”
        checkbox is checked.
        With this addon, the checkbox is unchecked by default.
    """,
    "version": "18.0.1.0.0",
    "category": "Helpdesk",
    "website": "https://github.com/OCA/helpdesk",
    "author": "Solvos, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["helpdesk_mgmt"],
    "assets": {
        "web.assets_backend": [
            "helpdesk_ticket_message_contact_default_unchecked/static/src/js/suggested_recipients_list.esm.js"
        ],
        "web.assets_tests": [
            "helpdesk_ticket_message_contact_default_unchecked/static/tests/tours/*",
        ],
    },
}
