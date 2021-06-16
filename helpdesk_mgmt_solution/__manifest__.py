# Copyright 2021 Sirum GmbH
# Copyright 2021 elego Software Solutions GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Solution",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "category": "Helpdesk",
    "application": False,
    "author": "Sirum GmbH, "
              "Elego Software Solutions GmbH, "
              "Odoo Community Association (OCA)",
    'summary': """
Create solutions for and assign them to Helpdesk Tickets
""",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_view.xml",
        "views/helpdesk_solution_view.xml",
        "wizard/solution.xml",
        "views/menu_view.xml",
    ],
    "demo": [
        "demo/helpdesk_solution_demo.xml",
    ],
    "installable": True,
    "auto_install": False,
}
