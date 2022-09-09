# Copyright (C) 2019 - TODAY, Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Helpdesk Mgmt Fieldservice Equipment",
    "summary": """
        Create service orders from a ticket""",
    "version": "14.0.1.1.0",
    "license": "LGPL-3",
    "author": "Open Source Integrators, "
    "Escodoo, "
    "Odoo Community Association (OCA)",
    "website": "",
    "depends": [
        "base",
        "mail",
        "portal",
        "helpdesk_mgmt",
        "fieldservice",
        "website",
        "base_maintenance"
        
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_templates.xml",
        "views/helpdesk_ticket_views.xml"
    ],
    "demo": []
}
