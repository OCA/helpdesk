# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Mgmt Fieldservice",
    "summary": """
        Create service orders from a ticket""",
    "version": "18.0.1.1.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, "
    "Escodoo, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": [
        "helpdesk_mgmt",
        "fieldservice",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_views.xml",
        "views/fsm_location_views.xml",
        "views/fsm_order_views.xml",
        "wizards/fsm_order_close_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "helpdesk_mgmt_fieldservice/static/src/scss/helpdesk_column.scss",
        ],
    },
    "demo": [],
}
