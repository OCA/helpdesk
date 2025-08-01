# Copyright 2025 Kencove (https://www.kencove.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Management Import",
    "summary": """
        Import data from helpdesk EE to helpdesk_mgmt CE
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "Services/Helpdesk",
    "author": "Kencove, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": [
        "helpdesk_type",
        "helpdesk_mgmt_sla",
        "helpdesk_mgmt_rating",
    ],
    "external_dependencies": {
        "python": ["openupgradelib"],
    },
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
