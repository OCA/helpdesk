# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Ticket Type",
    "version": "13.0.1.0.2",
    "license": "AGPL-3",
    "summary": "Add a type to your tickets",
    "author": "Konos, " "Open Source Integrators, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_type.xml",
        "views/helpdesk_ticket_team.xml",
        "views/helpdesk_ticket.xml",
    ],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["nelsonramirezs", "max3903"],
}
