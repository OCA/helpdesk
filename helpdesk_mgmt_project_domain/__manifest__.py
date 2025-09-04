# Copyright 2025 Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Mgmt Project Domain",
    "summary": """Enable to set a project domain on ticket""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "website": "https://github.com/OCA/helpdesk",
    "depends": [
        "helpdesk_mgmt_project",
    ],
    "data": [
        "views/helpdesk_ticket_view.xml",
        "views/helpdesk_ticket_team_view.xml",
        "views/res_config_settings.xml",
    ],
    "demo": [
        "demo/helpdesk_mgmt_project_domain_demo.xml",
    ],
}
