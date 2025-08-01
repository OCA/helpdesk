# Copyright 2025 Kencove (https://www.kencove.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Management Import Setup",
    "summary": """
        Setup: Clone the necessary tables to prepare for the migration
        and remove the EE helpdesk module
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "Services/Helpdesk",
    "author": "Kencove, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["mail"],
    "external_dependencies": {
        "python": ["openupgradelib"],
    },
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "post_load": "post_load_hook",
}
